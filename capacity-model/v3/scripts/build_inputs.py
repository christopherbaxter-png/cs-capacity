"""Aggregate the source exports into non-identifying team-book inputs.

Account population, tier, segment, region, ARR and renewal dates come from the
Vitally tab of the CX portfolio workbook ('nov18vitally raw data').

The team is the set of accounts whose Vitally CSM is on the team roster. The
roster is the CSM list in the accounts export. The export is used only for the
roster and for a comparison; it does not set account numbers.

The AM portfolio extract is used only to check coverage and to measure where AM
and Vitally disagree (ARR, market, and account owner).

Run locally with the three source files. Writes data/team_book.json, which the
calculator reads. No account names, IDs or emails leave this script.

Usage:
  python build_inputs.py CX_PORTFOLIO.xlsx AM_PORTFOLIO.xlsx ACCOUNTS_EXPORT.csv
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

REGION_BY_COUNTRY = {
    "GB": "UKI", "IE": "UKI",
    "DE": "DACH", "AT": "DACH", "CH": "DACH",
    "DK": "Nordics", "SE": "Nordics", "NO": "Nordics", "FI": "Nordics",
    "ES": "Iberia", "PT": "Iberia",
    "NL": "Benelux", "BE": "Benelux", "LU": "Benelux",
    "FR": "France & Italy", "IT": "France & Italy",
}
REGION_BY_AM_MARKET = {
    "UKI": "UKI", "DE": "DACH", "DK": "Nordics", "SE": "Nordics", "ES": "Iberia",
    "NL": "Benelux", "FR": "France & Italy", "OTHER MARKETS": "Other",
}
SEGMENT_LABEL = {"MM": "Mid Market", "UPMARKET": "Upmarket", "SMB": "SMB", "": "Unassigned"}
TIER_LABEL = {"P1": "P1", "P2": "P2", "P3": "P3", "P4": "P4", "": "Blank"}
# Regional and pool mailboxes. An owner of this kind is a group, not a person.
GROUP_MAILBOXES = {"customersuccess@pleo.io", "ukimm@pleo.io", "dachmm@pleo.io", "iberiamm@pleo.io"}


def name_tokens(text):
    s = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]", " ", s.replace(".", " ")).split()


def owner_tokens(email):
    return name_tokens(str(email).split("@")[0])


def main(cx_xlsx, am_xlsx, accounts_csv):
    cx = pd.read_excel(cx_xlsx, sheet_name="nov18vitally raw data", dtype=str).fillna("")
    am = pd.read_excel(am_xlsx, sheet_name="am_customer_extract", dtype={"company_id": str}).fillna("")
    exp = pd.read_csv(accounts_csv, dtype=str).fillna("")

    # Team = Vitally accounts whose CSM is on the team roster (CSM list in the accounts export).
    roster = set(exp["CSM"].str.lower()) - {""}
    cx["csm_l"] = cx["CSM"].str.lower()
    team = cx[cx["csm_l"].isin(roster)].copy()

    team["arr_eur"] = pd.to_numeric(team["vitally.custom.arrEur"], errors="coerce").fillna(0.0)
    team["region"] = team["account_country"].map(REGION_BY_COUNTRY).fillna("Other")
    team["segment"] = team["gtm_segment"].map(SEGMENT_LABEL).fillna("Unassigned")
    team["tier"] = team["vitally.custom.gtmPriorityTier"].map(TIER_LABEL).fillna("Blank")
    team["renewal"] = pd.to_datetime(team["hspot.zuora_termenddate"], errors="coerce")

    am["company_id"] = am["company_id"].astype(str)
    am_by_id = am.drop_duplicates("company_id").set_index("company_id")
    team["in_am"] = team["externalId"].isin(am_by_id.index)
    team["am_market"] = team["externalId"].map(am_by_id["market"]).fillna("")
    team["am_coverage"] = team["externalId"].map(am_by_id["csm_coverage"]).fillna("")
    team["am_csm_name"] = team["externalId"].map(am_by_id["csm_name"]).fillna("")
    team["am_arr"] = pd.to_numeric(team["externalId"].map(am_by_id["arr_current"]), errors="coerce").fillna(0.0)

    out = {
        "source": {
            "population": "Vitally tab, nov18vitally raw data (CX portfolio workbook). Team = accounts whose Vitally CSM is on the team roster.",
            "roster": "CSM names from the accounts export (used only to define the team roster).",
            "cx_rows": int(len(cx)),
            "team_accounts": int(len(team)),
            "am_rows": int(len(am)),
            "note": "Tier, segment, region, ARR and renewal dates from Vitally. AM used for coverage and conflict checks only.",
        },
    }

    g = team.groupby(["segment", "tier"]).agg(accounts=("externalId", "size"), arr_eur=("arr_eur", "sum")).reset_index()
    out["accounts_by_segment_tier"] = g[["segment", "tier", "accounts"]].to_dict("records")
    out["arr_by_segment_tier"] = [
        {"segment": r.segment, "tier": r.tier, "arr_eur": round(float(r.arr_eur), 2)} for r in g.itertuples()]

    rst = team.groupby(["region", "segment", "tier"]).agg(
        accounts=("externalId", "size"), arr_eur=("arr_eur", "sum")).reset_index()
    out["region_segment_tier"] = [
        {"region": r.region, "segment": r.segment, "tier": r.tier,
         "accounts": int(r.accounts), "arr_eur": round(float(r.arr_eur), 2)} for r in rst.itertuples()]

    r27 = team[team["renewal"].dt.year == 2027].copy()
    r27["month"] = r27["renewal"].dt.month
    rm = r27.groupby(["segment", "tier", "month"]).size().reset_index(name="renewals")
    out["renewals_2027"] = rm.to_dict("records")
    out["renewals_2027_by_month_tier"] = rm.groupby(["tier", "month"]).renewals.sum().reset_index().to_dict("records")

    bands = [0, 5000, 10000, 20000, 50000, 100000, float("inf")]
    labels = ["<5k", "5k-10k", "10k-20k", "20k-50k", "50k-100k", "100k+"]
    mg = team[team["tier"].isin(["P1", "P2"])].copy()
    mg["band"] = pd.cut(mg["arr_eur"], bands, labels=labels, right=False)
    ab = mg.groupby(["segment", "tier", "band"], observed=False).agg(
        accounts=("externalId", "size"), arr_eur=("arr_eur", "sum")).reset_index()
    out["managed_arr_bands"] = [
        {"segment": r.segment, "tier": r.tier, "band": str(r.band),
         "accounts": int(r.accounts), "arr_eur": round(float(r.arr_eur), 2)} for r in ab.itertuples()]

    conc = {}
    for seg, d in team.groupby("segment"):
        v = d["arr_eur"].sort_values(ascending=False)
        top = v.iloc[: max(1, int(round(len(v) * 0.10)))]
        conc[seg] = {"accounts": int(len(v)), "top10pct_accounts": int(len(top)),
                     "top10pct_arr_share": round(float(top.sum() / v.sum()), 4) if v.sum() else 0}
    out["arr_concentration"] = conc
    out["renewals_2027_total"] = int(len(r27))
    out["renewals_blank_date"] = int(team["renewal"].isna().sum())

    cov = team.groupby("tier").agg(
        accounts=("externalId", "size"),
        in_am_extract=("in_am", "sum"),
        named_csm_in_am=("am_coverage", lambda s: int((s == "named CSM").sum())),
        former_employee_in_am=("am_coverage", lambda s: int((s == "former employee").sum())),
    ).reset_index()
    out["coverage"] = cov.to_dict("records")

    # ---- AM vs Vitally conflicts (team accounts that match AM on externalId) ----
    m = team[team["in_am"]].copy()
    both = m[(m["am_arr"] > 0) & (m["arr_eur"] > 0)]
    diff = (both["am_arr"] - both["arr_eur"]).abs()
    arr_differs = diff > 0.01 * both[["am_arr", "arr_eur"]].max(axis=1)

    compared_market = m[(m["am_market"] != "") & (m["am_market"].isin(REGION_BY_AM_MARKET))]
    # AM's "OTHER MARKETS" covers countries this model maps to a named region (e.g. AT, NO, PT), so it is a taxonomy gap, not a conflict.
    other_markets = compared_market["am_market"] == "OTHER MARKETS"
    market_mismatch = compared_market[(~other_markets) & (compared_market["am_market"].map(REGION_BY_AM_MARKET) != compared_market["region"])]

    am_named = m[m["am_coverage"] == "named CSM"]
    vit_group = am_named["csm_l"].isin(GROUP_MAILBOXES) | (am_named["CSM"] == "")
    am_named_person = am_named[~vit_group]
    # Two names agree if they share a token of two or more letters. This allows for nicknames (Bart/Bartosz),
    # initials (J Diego/Diego), double or changed surnames and email local parts that hold only a first name.
    pairs = [(owner_tokens(a), name_tokens(b)) for a, b in
             zip(am_named_person["csm_l"], am_named_person["am_csm_name"])]
    pairs = [(o, n) for o, n in pairs if o and n]
    name_agree = [any(len(t) > 1 and t in set(n) for t in o) for o, n in pairs]
    am_pool = m[m["am_coverage"] == "CS pool"]
    pool_vit_person = am_pool[~am_pool["csm_l"].isin(GROUP_MAILBOXES) & (am_pool["CSM"] != "")]

    # Export comparison: same roster, same accounts, tiers as recorded in each source.
    exp_ids = set(exp["externalId"])
    tier_overlap = team[team["externalId"].isin(exp_ids)].merge(
        exp[["externalId", "gtm_priority_tier"]], on="externalId")
    tier_agree = (tier_overlap["vitally.custom.gtmPriorityTier"] == tier_overlap["gtm_priority_tier"]).mean()
    out["source_conflicts"] = {
        "team_accounts": int(len(team)),
        "matched_in_am": int(len(m)),
        "not_in_am": int(len(team) - len(m)),
        "arr_both_positive": int(len(both)),
        "arr_differs_over_1pct": int(arr_differs.sum()),
        "arr_abs_diff_eur": round(float(diff[arr_differs].sum()), 2),
        "arr_only_in_am": int(((m["am_arr"] > 0) & (m["arr_eur"] == 0)).sum()),
        "arr_only_in_vitally": int(((m["arr_eur"] > 0) & (m["am_arr"] == 0)).sum()),
        "market_compared": int(len(compared_market)),
        "market_differs_from_vitally_region": int(len(market_mismatch)),
        "market_other_markets_for_named_region_country": int((other_markets & (compared_market["region"] != "Other")).sum()),
        "owner_am_named_vitally_group_or_blank": int(vit_group.sum()),
        "owner_am_named_vitally_person": int(len(am_named_person)),
        "owner_name_agrees": int(sum(name_agree)),
        "owner_name_no_shared_token": int(len(name_agree) - sum(name_agree)),
        "owner_am_pool_vitally_person": int(len(pool_vit_person)),
        "owner_am_former_employee": int((m["am_coverage"] == "former employee").sum()),
    }
    out["export_comparison"] = {
        "accounts_export_rows": int(len(exp)),
        "team_in_export": int(team["externalId"].isin(exp_ids).sum()),
        "team_not_in_export": int((~team["externalId"].isin(exp_ids)).sum()),
        "export_not_in_team": int(len(exp_ids - set(team["externalId"]))),
        "tier_agreement_on_overlap": round(float(tier_agree), 4),
        "export_blank_tiers": int((exp["gtm_priority_tier"] == "").sum()),
        "vitally_blank_tiers_in_team": int((team["tier"] == "Blank").sum()),
    }

    out["headline"] = {
        "total_accounts": int(len(team)),
        "total_arr_eur": round(float(team["arr_eur"].sum()), 2),
        "managed_book_P1_P2_accounts": int(team["tier"].isin(["P1", "P2"]).sum()),
        "pool_book_P3_P4_accounts": int(team["tier"].isin(["P3", "P4"]).sum()),
        "blank_tier_accounts": int((team["tier"] == "Blank").sum()),
        "fy26_expansion_baseline_eur": 17_700_000,
        "fy26_lost_arr_baseline_eur": 18_000_000,
        "source_fy26_baselines": "CX Strategy Offsite agenda (Nov 2026), 'The strategy in 30 seconds'. 2027 targets are shown as TBD in the source.",
    }

    dest = Path(__file__).resolve().parent.parent / "data" / "team_book.json"
    dest.write_text(json.dumps(out, indent=2, default=str))
    print("wrote", dest)
    print(json.dumps({"headline": out["headline"], "source_conflicts": out["source_conflicts"],
                      "export_comparison": out["export_comparison"]}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])

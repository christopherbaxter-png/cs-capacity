"""Aggregate the source exports into non-identifying Mid Market and Upmarket inputs.

Account population, tARR, segment, country and renewal dates come from the Vitally tab
of the CX portfolio workbook ('nov18vitally raw data').

The team is the set of accounts whose Vitally CSM is on the team roster. The roster is
the CSM list in the accounts export. The export is used only for the roster and for a
comparison; it does not set account numbers.

Regions follow the Nov 2026 portfolio review ('Country Analysis'): UKI, Nordics,
Central & South, Rest of World.

Headcount by region comes from the review's 'Portfolio by CSM' tab, counted as aggregates.
CSM names are not written to the output.

The AM portfolio extract is used only for coverage and conflict checks.

Usage:
  python build_inputs.py CX_PORTFOLIO.xlsx AM_PORTFOLIO.xlsx ACCOUNTS_EXPORT.csv
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

# Review region mapping by account country (Country Analysis tab).
REGION_BY_COUNTRY = {
    "GB": "UKI", "IE": "UKI", "JE": "UKI",
    "DK": "Nordics", "SE": "Nordics", "NO": "Nordics", "FI": "Nordics", "FO": "Nordics", "GL": "Nordics",
    "DE": "Central & South", "ES": "Central & South", "NL": "Central & South", "FR": "Central & South",
    "AT": "Central & South", "MT": "Central & South", "PT": "Central & South", "IT": "Central & South",
    "BE": "Central & South", "LU": "Central & South", "EE": "Central & South", "PL": "Central & South",
    "RO": "Central & South", "LT": "Central & South",
}
REGIONS = ["UKI", "Nordics", "Central & South", "Rest of World"]
REGION_BY_AM_MARKET = {
    "UKI": "UKI", "DE": "Central & South", "DK": "Nordics", "SE": "Nordics", "ES": "Central & South",
    "NL": "Central & South", "FR": "Central & South", "OTHER MARKETS": "Rest of World",
}
# tARR bin edges (EUR). Covers the four priority tiers (3.5k, 12k, 36k) and the 5k, 10k and 20k thresholds.
BIN_EDGES = [0, 3500, 5000, 10000, 12000, 20000, 36000]
SEGMENT_OF = {"MM": "Mid Market", "UPMARKET": "Upmarket"}
GROUP_MAILBOXES = {"customersuccess@pleo.io", "ukimm@pleo.io", "dachmm@pleo.io", "iberiamm@pleo.io"}


def name_tokens(text):
    s = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]", " ", s.replace(".", " ")).split()


def owner_tokens(email):
    return name_tokens(str(email).split("@")[0])


def headcount_from_review(path):
    """Count named CSMs per review region. Counts only; no names are written."""
    pc = pd.read_excel(path, sheet_name="Portfolio by CSM", dtype=str, header=None).fillna("")
    out = {r: {"active_mm_um_csms": 0, "active_smb_primary_csms": 0, "multi_region_mm_um_csms": 0,
               "deactivated_csms_holding_mm_um_accounts": 0, "mm_um_accounts_held_by_deactivated": 0}
           for r in REGIONS + ["Multi-region"]}
    for i, r in pc.iterrows():
        if i < 5 or i > 90:
            continue
        try:
            count = int(float(r[4]))
        except (ValueError, TypeError):
            continue
        region, seg, note = str(r[2]).strip(), str(r[3]).strip(), str(r[15])
        um, mm = int(float(r[9] or 0)), int(float(r[10] or 0))
        deact = "deactivated" in note.lower()
        key = region if region in out else None
        if key is None:
            continue
        if deact:
            if um + mm > 0:
                out[key]["deactivated_csms_holding_mm_um_accounts"] += 1
                out[key]["mm_um_accounts_held_by_deactivated"] += um + mm
            continue
        if seg in ("MM", "UM"):
            if key == "Multi-region":
                out[key]["multi_region_mm_um_csms"] += 1
            else:
                out[key]["active_mm_um_csms"] += 1
        elif seg == "SMB":
            out[key]["active_smb_primary_csms"] += 1
    return out


def main(cx_xlsx, am_xlsx, accounts_csv):
    cx = pd.read_excel(cx_xlsx, sheet_name="nov18vitally raw data", dtype=str).fillna("")
    am = pd.read_excel(am_xlsx, sheet_name="am_customer_extract", dtype={"company_id": str}).fillna("")
    exp = pd.read_csv(accounts_csv, dtype=str).fillna("")

    roster = set(exp["CSM"].str.lower()) - {""}
    cx["csm_l"] = cx["CSM"].str.lower()
    team = cx[cx["csm_l"].isin(roster)].copy()

    team["arr_eur"] = pd.to_numeric(team["vitally.custom.arrEur"], errors="coerce").fillna(0.0)
    team["tarr_eur"] = pd.to_numeric(team["vitally.custom.tarr"], errors="coerce").fillna(0.0)
    team["region"] = team["account_country"].map(REGION_BY_COUNTRY).fillna("Rest of World")
    team["segment"] = team["gtm_segment"].map(SEGMENT_OF).fillna("Other")
    team["renewal"] = pd.to_datetime(team["hspot.zuora_termenddate"], errors="coerce")
    team["bin"] = np.searchsorted(BIN_EDGES, team["tarr_eur"].values, side="right") - 1

    am["company_id"] = am["company_id"].astype(str)
    am_by_id = am.drop_duplicates("company_id").set_index("company_id")
    team["in_am"] = team["externalId"].isin(am_by_id.index)
    team["am_market"] = team["externalId"].map(am_by_id["market"]).fillna("")
    team["am_coverage"] = team["externalId"].map(am_by_id["csm_coverage"]).fillna("")
    team["am_csm_name"] = team["externalId"].map(am_by_id["csm_name"]).fillna("")
    team["am_arr"] = pd.to_numeric(team["externalId"].map(am_by_id["arr_current"]), errors="coerce").fillna(0.0)

    mm = team[team["segment"].isin(SEGMENT_OF.values())].copy()

    # Accounts, tARR and ARR by segment, region and tARR bin.
    g = mm.groupby(["segment", "region", "bin"]).agg(
        accounts=("externalId", "size"), tarr_eur=("tarr_eur", "sum"), arr_eur=("arr_eur", "sum")).reset_index()
    bins = [{"segment": r.segment, "region": r.region, "bin": int(r.bin), "accounts": int(r.accounts),
             "tarr_eur": round(float(r.tarr_eur), 2), "arr_eur": round(float(r.arr_eur), 2)} for r in g.itertuples()]

    # 2027 renewals for MM/UM accounts, by segment, region, tARR bin and month.
    r27 = mm[mm["renewal"].dt.year == 2027].copy()
    r27["month"] = r27["renewal"].dt.month
    rg = r27.groupby(["segment", "region", "bin", "month"]).size().reset_index(name="renewals")
    renewals = [{"segment": r.segment, "region": r.region, "bin": int(r.bin), "month": int(r.month),
                 "renewals": int(r.renewals)} for r in rg.itertuples()]

    # Priority tiers from the four-tier image, applied to tARR. Image P2 floor is 12k.
    def tier_of(x):
        return "P1" if x >= 36000 else "P2" if x >= 12000 else "P3" if x >= 3500 else "P4"
    mm["image_tier"] = mm["tarr_eur"].map(tier_of)

    # ---- AM vs Vitally conflicts (team accounts that match AM on externalId) ----
    m = team[team["in_am"]].copy()
    both = m[(m["am_arr"] > 0) & (m["arr_eur"] > 0)]
    diff = (both["am_arr"] - both["arr_eur"]).abs()
    arr_differs = diff > 0.01 * both[["am_arr", "arr_eur"]].max(axis=1)
    compared_market = m[(m["am_market"] != "") & (m["am_market"].isin(REGION_BY_AM_MARKET))]
    other_markets = compared_market["am_market"] == "OTHER MARKETS"
    market_mismatch = compared_market[(~other_markets) & (compared_market["am_market"].map(REGION_BY_AM_MARKET) != compared_market["region"])]
    am_named = m[m["am_coverage"] == "named CSM"]
    vit_group = am_named["csm_l"].isin(GROUP_MAILBOXES) | (am_named["CSM"] == "")
    am_named_person = am_named[~vit_group]
    pairs = [(owner_tokens(a), name_tokens(b)) for a, b in
             zip(am_named_person["csm_l"], am_named_person["am_csm_name"])]
    pairs = [(o, n) for o, n in pairs if o and n]
    name_agree = [any(len(t) > 1 and t in set(n) for t in o) for o, n in pairs]
    am_pool = m[m["am_coverage"] == "CS pool"]
    exp_ids = set(exp["externalId"])
    tier_overlap = team[team["externalId"].isin(exp_ids)].merge(exp[["externalId", "gtm_priority_tier"]], on="externalId")
    tier_agree = (tier_overlap["vitally.custom.gtmPriorityTier"] == tier_overlap["gtm_priority_tier"]).mean()
    adoption_differs = int((team["Adoption CSM"].str.lower() != team["csm_l"]).sum())

    out = {
        "source": {
            "population": "Vitally tab, nov18vitally raw data (CX portfolio workbook). Team = accounts whose Vitally CSM is on the team roster.",
            "roster": "CSM names from the accounts export (used only to define the roster).",
            "regions": "Country mapping from the Nov 2026 portfolio review, Country Analysis tab.",
            "headcount": "Nov 2026 portfolio review, Portfolio by CSM tab. Counts only; no names.",
            "tarr": "vitally.custom.tarr. Priority tiers and the managed threshold use tARR.",
            "cx_rows": int(len(cx)),
            "team_accounts": int(len(team)),
            "mm_um_accounts": int(len(mm)),
        },
        "bin_edges": BIN_EDGES,
        "mm_um_bins": bins,
        "mm_um_renewals_2027": renewals,
        "mm_um_renewals_blank_date": int(mm["renewal"].isna().sum()),
        "mm_um_image_tiers": mm.groupby(["segment", "region", "image_tier"]).agg(
            accounts=("externalId", "size"), tarr_eur=("tarr_eur", "sum")).reset_index().to_dict("records"),
        "headcount_review": headcount_from_review(cx_xlsx),
        "source_conflicts": {
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
            "market_other_markets_for_named_region_country": int((other_markets & (compared_market["region"] != "Rest of World")).sum()),
            "owner_am_named_vitally_group_or_blank": int(vit_group.sum()),
            "owner_am_named_vitally_person": int(len(am_named_person)),
            "owner_name_agrees": int(sum(name_agree)),
            "owner_name_no_shared_token": int(len(name_agree) - sum(name_agree)),
            "owner_am_pool_vitally_person": int((~am_pool["csm_l"].isin(GROUP_MAILBOXES) & (am_pool["CSM"] != "")).sum()),
            "owner_am_former_employee": int((m["am_coverage"] == "former employee").sum()),
            "adoption_csm_differs_from_csm": adoption_differs,
        },
        "export_comparison": {
            "accounts_export_rows": int(len(exp)),
            "team_in_export": int(team["externalId"].isin(exp_ids).sum()),
            "team_not_in_export": int((~team["externalId"].isin(exp_ids)).sum()),
            "export_not_in_team": int(len(exp_ids - set(team["externalId"]))),
            "tier_agreement_on_overlap": round(float(tier_agree), 4),
            "export_blank_tiers": int((exp["gtm_priority_tier"] == "").sum()),
        },
        "headline": {
            "team_accounts": int(len(team)),
            "team_arr_eur": round(float(team["arr_eur"].sum()), 2),
            "team_tarr_eur": round(float(team["tarr_eur"].sum()), 2),
            "mm_um_accounts": int(len(mm)),
            "mm_um_arr_eur": round(float(mm["arr_eur"].sum()), 2),
            "fy26_expansion_baseline_eur": 17_700_000,
            "fy26_lost_arr_baseline_eur": 18_000_000,
            "source_fy26_baselines": "CX Strategy Offsite agenda (Nov 2026). 2027 targets are shown as TBD in the source.",
        },
    }

    dest = Path(__file__).resolve().parent.parent / "data" / "team_book.json"
    dest.write_text(json.dumps(out, indent=2, default=str))
    print("wrote", dest)
    print(json.dumps({"headline": out["headline"], "headcount_review": out["headcount_review"],
                      "source_conflicts": out["source_conflicts"]}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])

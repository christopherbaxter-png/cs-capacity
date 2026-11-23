"""Aggregate the source exports into non-identifying team-book inputs.

Run locally with the three source files. Writes data/team_book.json, which the
calculator reads. No account names, IDs or CSM emails leave this script.

Usage:
  python build_inputs.py ACCOUNTS.csv CX_PORTFOLIO.xlsx AM_PORTFOLIO.xlsx
"""
import json
import sys
from collections import Counter, defaultdict
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
SEGMENT_LABEL = {"MM": "Mid Market", "UPMARKET": "Upmarket", "SMB": "SMB", "": "Unassigned"}
TIER_LABEL = {"P1": "P1", "P2": "P2", "P3": "P3", "P4": "P4", "": "Blank"}


def main(accounts_csv, cx_xlsx, am_xlsx):
    acc = pd.read_csv(accounts_csv, dtype=str).fillna("")
    cx = pd.read_excel(cx_xlsx, sheet_name="nov18vitally raw data", dtype=str).fillna("")
    am = pd.read_excel(am_xlsx, sheet_name="am_customer_extract", dtype={"company_id": str}).fillna("")

    # Team book = the 7,813 accounts in the accounts export. ARR from CX (accounts export TARR is mostly blank).
    arr = cx.set_index("externalId")["vitally.custom.arrEur"]
    acc["arr_eur"] = pd.to_numeric(acc["externalId"].map(arr), errors="coerce").fillna(0.0)
    acc["region"] = acc["account_country"].map(REGION_BY_COUNTRY).fillna("Other")
    acc["segment"] = acc["gtm_segment"].map(SEGMENT_LABEL).fillna("Unassigned")
    acc["tier"] = acc["gtm_priority_tier"].map(TIER_LABEL).fillna("Blank")
    acc["renewal"] = pd.to_datetime(acc["hspot.zuora_termenddate"], errors="coerce")

    am["company_id"] = am["company_id"].astype(str)
    am_by_id = am.drop_duplicates("company_id").set_index("company_id")
    acc["in_am"] = acc["externalId"].isin(am_by_id.index)
    acc["am_market"] = acc["externalId"].map(am_by_id["market"]).fillna("")
    acc["am_coverage"] = acc["externalId"].map(am_by_id["csm_coverage"]).fillna("")

    out = {
        "source": {
            "accounts_rows": int(len(acc)),
            "cx_rows": int(len(cx)),
            "am_rows": int(len(am)),
            "note": "Team book = accounts export (7,813). ARR from CX vitally.custom.arrEur. AM coverage shown for accounts that match on externalId.",
        },
        "accounts_by_segment_tier": [],
        "arr_by_segment_tier": [],
        "region_segment_tier": [],
        "renewals_2027": [],
        "renewals_2027_by_month_tier": [],
        "managed_arr_bands": [],
        "arr_concentration": {},
        "coverage": [],
        "headline": {},
    }

    g = acc.groupby(["segment", "tier"]).agg(accounts=("externalId", "size"), arr_eur=("arr_eur", "sum")).reset_index()
    out["accounts_by_segment_tier"] = g[["segment", "tier", "accounts"]].to_dict("records")
    out["arr_by_segment_tier"] = [
        {"segment": r.segment, "tier": r.tier, "arr_eur": round(float(r.arr_eur), 2)} for r in g.itertuples()
    ]

    # Region x segment x tier: lets the calculator filter by region and segment.
    rst = acc.groupby(["region", "segment", "tier"]).agg(
        accounts=("externalId", "size"), arr_eur=("arr_eur", "sum")).reset_index()
    out["region_segment_tier"] = [
        {"region": r.region, "segment": r.segment, "tier": r.tier,
         "accounts": int(r.accounts), "arr_eur": round(float(r.arr_eur), 2)}
        for r in rst.itertuples()]

    # 2027 renewal calendar by segment and tier (renewal date from Zuora term end).
    r27 = acc[acc["renewal"].dt.year == 2027].copy()
    r27["month"] = r27["renewal"].dt.month
    rm = r27.groupby(["segment", "tier", "month"]).size().reset_index(name="renewals")
    out["renewals_2027"] = rm.to_dict("records")
    out["renewals_2027_by_month_tier"] = rm.groupby(["tier", "month"]).renewals.sum().reset_index().to_dict("records")

    # ARR bands for pooling thresholds (managed tiers only: P1 and P2).
    bands = [0, 5000, 10000, 20000, 50000, 100000, float("inf")]
    labels = ["<5k", "5k-10k", "10k-20k", "20k-50k", "50k-100k", "100k+"]
    mg = acc[acc["tier"].isin(["P1", "P2"])].copy()
    mg["band"] = pd.cut(mg["arr_eur"], bands, labels=labels, right=False)
    ab = mg.groupby(["segment", "tier", "band"], observed=False).agg(
        accounts=("externalId", "size"), arr_eur=("arr_eur", "sum")).reset_index()
    out["managed_arr_bands"] = [
        {"segment": r.segment, "tier": r.tier, "band": str(r.band),
         "accounts": int(r.accounts), "arr_eur": round(float(r.arr_eur), 2)}
        for r in ab.itertuples()]

    # Revenue concentration: share of segment ARR in the top 10% of accounts.
    conc = {}
    for seg, d in acc.groupby("segment"):
        v = d["arr_eur"].sort_values(ascending=False)
        top = v.iloc[: max(1, int(round(len(v) * 0.10)))]
        conc[seg] = {"accounts": int(len(v)), "top10pct_accounts": int(len(top)),
                     "top10pct_arr_share": round(float(top.sum() / v.sum()), 4) if v.sum() else 0}
    out["arr_concentration"] = conc
    out["renewals_2027_total"] = int(len(r27))
    out["renewals_blank_date"] = int(acc["renewal"].isna().sum())

    cov = acc.assign(in_am_flag=acc["in_am"]).groupby(["tier"]).agg(
        accounts=("externalId", "size"),
        in_am_extract=("in_am", "sum"),
        named_csm_in_am=("am_coverage", lambda s: int((s == "named CSM").sum())),
        former_employee_in_am=("am_coverage", lambda s: int((s == "former employee").sum())),
    ).reset_index()
    out["coverage"] = cov.to_dict("records")

    out["headline"] = {
        "total_accounts": int(len(acc)),
        "total_arr_eur": round(float(acc["arr_eur"].sum()), 2),
        "managed_book_P1_P2_accounts": int(acc["tier"].isin(["P1", "P2"]).sum()),
        "pool_book_P3_P4_accounts": int(acc["tier"].isin(["P3", "P4"]).sum()),
        "blank_tier_accounts": int((acc["tier"] == "Blank").sum()),
        "fy26_expansion_baseline_eur": 17_700_000,
        "fy26_lost_arr_baseline_eur": 18_000_000,
        "source_fy26_baselines": "CX Strategy Offsite agenda (Nov 2026), 'The strategy in 30 seconds'. 2027 targets are shown as TBD in the source.",
    }

    dest = Path(__file__).resolve().parent.parent / "data" / "team_book.json"
    dest.write_text(json.dumps(out, indent=2, default=str))
    print("wrote", dest)
    print(json.dumps(out["headline"], indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])

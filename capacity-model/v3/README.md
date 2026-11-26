# CSM capacity calculator, v4 (prototype)

A single-page calculator for 2027 CSM capacity in the Mid Market and Upmarket (MM/UM) team. SMB is excluded, since product-led growth covers it.

It answers one question: how many CSMs the MM/UM book needs, with accounts at or above a tARR threshold fully CSM-managed and the rest pooled. The result is shown by leader region, next to the CSMs the Nov 2026 review shows in each region.

Open `index.html` in a browser. It has no dependencies and no server. Data is embedded, and nothing is sent anywhere.

## Status: read before using

- **Hours per account are placeholders, and they drive almost all of the result.** At the default 12,000 tARR threshold the calculator shows 40.8 managed and 11.8 pool CSMs needed (52.7 in total), with 1 hour per managed renewal and 30 minutes per pooled renewal, against 25 active MM/UM CSMs in the review. Do not act on the gap until the hours are calibrated. Gong's recorded call time for the sampled CSMs is about 4 hours per CSM per month, far below the modelled demand.
- **The threshold is the brief's, but tARR is unconfirmed.** Team tARR is about EUR 87.5m against EUR 44.9m of ARR. Confirm what tARR measures before the tiers are used for the managed split.
- **Leaders and available CSMs.** The base is the org chart, which is the 2027 team: 27 named ICs (UKI 11, Nordics 7, Central & South 9) and 3 open roles (UKI 2, Nordics 1). UKI is led by Tom Macbride. Stina Grahn is on maternity leave, and Jakob Klöfver manages Nordics while owning a book; his management share is a leader-time input, 0 until set. Nikol Rej Notlev is marked vacant on the chart, which would make Nordics 6 filled. The review's 26 active MM/UM CSMs differ from the chart: some have no accounts yet, and some have left.
- **The 2027 targets come from the project brief, not a finance source.** SLG EUR 5.5m, PLG EUR 12.6m and LARR EUR 18.2m are inputs. The model reads expansion as SLG + PLG and the lost-ARR budget as LARR. Both readings need confirming.
- **The CX Capacity Model is an example, not a spec.** Values marked ILLUSTRATIVE in `config/profiles.json` come from it and are not validated for this team.

## Segmentation

Accounts are tiered on Vitally's `vitally.custom.tarr`, using the four-tier image:

| Tier | tARR band | Book |
|---|---|---|
| P1 | 36,000 and above | Managed (CSM named) |
| P2 | 12,000 to 36,000 | Managed (CSM named) |
| P3 | 3,500 to 12,000 | Pooled |
| P4 | Below 3,500 | Pooled |

The managed threshold is a selectable input, from 3,500 to 36,000 tARR. The default is 12,000, the image's P2 floor, so P1 and P2 are managed and P3 and P4 are pooled. A 10,000 threshold would move about 240 P3 accounts into managed.

## Files

| File | Purpose |
|---|---|
| `index.html` | The calculator. Generated; do not edit by hand. |
| `calculator.template.html` | Source for the calculator. Edit this, then rebuild. |
| `config/profiles.json` | Defaults for hours, targets, targets from the brief, and the org chart, each with a source or a PLACEHOLDER or ILLUSTRATIVE flag. |
| `data/team_book.json` | Aggregated inputs: bins, renewals, tiers by region, review headcount and conflicts. No account names, IDs or emails. |
| `scripts/build_inputs.py` | Builds `data/team_book.json` from the source exports. |
| `scripts/build_calculator.py` | Builds `index.html` from the template, config and data. |
| `CHANGELOG.md` | What changed in each revision. |

## Rebuild

```bash
cd capacity-model/v3
# 1. Re-aggregate from the source exports (run locally; the exports stay outside the repo)
python scripts/build_inputs.py CX_PORTFOLIO.xlsx AM_PORTFOLIO.xlsx ACCOUNTS_EXPORT.csv
# 2. Rebuild the calculator
python scripts/build_calculator.py
```

The v2 workbook and calculator in the parent folder are unchanged and kept for reference.

## How the model works

**1. Accounts.** Counts and tARR for each tier, region and book come from `data/team_book.json`. The population is the Vitally accounts whose CSM is on the roster: 8,270 accounts, of which 4,711 are MM/UM. The 3,559 SMB or unsegmented accounts are excluded.

**2. Demand.** Hours per account-month by activity:

| Activity type | Hours per account-month |
|---|---|
| `share` | share of book active x hours per active account |
| `touchpoints` | touches per year / 12 x (hours per touch + extra hours per additional stakeholder) |
| `per_month` | hours per account-month |
| `per_year` | hours per account-year / 12 |
| `onboarding_total` | total hours / months in the onboarding window |

The managed book's buffer (15%, illustrative) is added to its activities. The pool buffer is 0. Renewals are added separately, as hours per renewal x renewals in each month from the 2027 Zuora term-end dates. P3 and P4 renewals sit with the pool, as confirmed on 26 Nov 2026. 1,024 MM/UM accounts have no renewal date and are excluded.

**3. Capacity.** Effective hours per CSM = contracted hours x portfolio share x availability (150 x 70% x 100% = 105 by default).

**4. CSMs needed.** Average monthly demand divided by (effective hours x target utilisation). Targets are 85% for managed and 80% for the pool, both from the v2 project instructions. The peak month is shown alongside the average.

**5. Regions and leaders.** Accounts are assigned to the review's regions: UKI, Nordics, Central & South, and Rest of World. Leaders are UKI: Tom Macbride, and Nordics: Jakob Klöfver (acting). Available CSMs are the org chart's named ICs, less leader time. Open roles are counted only in the gap incl. open roles. Rest of World has 38 MM/UM accounts and no named leader or CSM.

**6. Attrition check.** Company rates are applied to the MM/UM ARR in scope: lost ARR = LARR / company ARR (20.7%), and expansion = (SLG + PLG) / company ARR (20.6%). This is a drift check against the budget, not a segment forecast.

## Sources

| Input | Source |
|---|---|
| Accounts, tARR, ARR, country, segment, CSM, 2027 renewal dates | Nov 2026 CX portfolio review, Vitally tab `nov18vitally raw data` (`vitally.custom.tarr`, `vitally.custom.arrEur`, `hspot.zuora_termenddate`) |
| Tier bands and coverage model (P1 to P4) | "Implementing Four Priority Tiers" image |
| Region mapping (review); 2027 CSM counts and open roles (org chart) | Nov 2026 CX portfolio review: Country Analysis; Enterprise org chart (image) |
| Leaders, named ICs, open and vacant roles | Enterprise org chart (image) |
| Team roster (45 CSM names) | CSM list in the accounts export. Used only to define the team. Needs confirming. |
| AM coverage and conflict checks | AM portfolio extract (`am_customer_extract`). Not used for account numbers. |
| Contracted hours, portfolio share, targets, managed/pool split | Project instructions (v2). The 70% portfolio share also matches the CX example. |
| 2027 targets: SLG EUR 5.5m, PLG EUR 12.6m, LARR EUR 18.2m | Project brief. Interpreted, not confirmed. |
| Company ARR base (EUR 87.9m) | CX offsite agenda, Nov 2026 |
| Average expansion deal (EUR 12.8k) | CX Capacity Model WIP tab, USD 12,000 to 12,800. Placeholder; currency unconfirmed. |
| Hours per account, touch cadence, buffer | PLACEHOLDER or ILLUSTRATIVE. Structure from the CX Capacity Model example; not validated for this team. |

## Open decisions

1. **Managed threshold.** Set at 12,000 tARR, the image's P2 floor (confirmed 26 Nov 2026). 10,000 remains selectable in the calculator.
2. **tARR definition.** Confirm what tARR measures, and whether tiers should use it rather than ARR.
3. **P3 and P4 renewals.** Confirmed: the pool handles them.
4. **Target utilisation** for each book (85% and 80% are the v2 placeholders).
5. **Roster.** The base is the org chart: 27 named ICs and 3 open roles. Confirm Aida Selam's place on the chart, Nikol Rej Notlev's vacancy, and whether the UKI vacant senior role should count. Enter Jakob's management share.
6. **Deactivated CSMs** still hold 148 MM/UM accounts. These need reassigning.
7. **Adoption CSM vs CSM.** 224 accounts have a different Adoption CSM from the CSM field. The review counts by Adoption CSM; this model uses CSM.
8. **Rest of World.** 38 MM/UM accounts have no leader. Confirm where they belong.
9. **Renewal dates.** 1,024 MM/UM accounts have no 2027 renewal date, so renewal hours are understated.
10. **Hours per account.** A two-week time study by tier is the largest open item.
11. **Targets.** Confirm what SLG, PLG and LARR mean, and the currency of the expansion deal size.
12. **FY27 headcount plan.** The model does not yet have a target headcount.

## Considerations for the next revision

- **Calibration first.** Replace the placeholder hours with a time study by tier. Gong call data can cross-check it.
- **Availability and attrition.** Holidays, sickness, meetings, internal time, attrition and ramp are not modelled.
- **Reactive load.** It is a percentage buffer for now. Ticket, escalation and fraud volumes per account per month would make it bottom-up.
- **Region allocation.** The model compares demand with CSM counts by review region. It does not model which accounts each CSM actually holds.
- **Privacy.** `data/team_book.json` holds aggregates only. Keep account-level exports out of the repo.

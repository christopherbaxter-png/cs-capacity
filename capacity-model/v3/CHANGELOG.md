# Changelog

## v4 (prototype), 26 Nov 2026

Narrows the calculator to Mid Market and Upmarket, and sizes the managed and pooled books by tARR tier and leader region.

- **Scope:** SMB and the Onboarding population are removed, since PLG covers SMB. The SMB and Onboarding profiles, headcount and hires, ramp, growth, annual churn, FY26 expansion and pool churn inputs are removed.
- **Segmentation:** the four priority tiers from the "Implementing Four Priority Tiers" image, applied to `vitally.custom.tarr` (P1 36k and above, P2 12k to 36k, P3 3.5k to 12k, P4 below 3.5k). The managed threshold is selectable, from 3.5k to 36k tARR, with 12,000 as the default (the image's P2 floor). Accounts at or above it are managed; the rest are pooled.
- **Regions and leaders:** accounts mapped to the review's regions. Leaders: UKI, Tom Macbride; Nordics, Jakob Klöfver (acting), with Stina Grahn on maternity leave. Available CSMs are the org chart's named ICs (UKI 11, Nordics 7, Central & South 9), the 2027 team, less leader time. Open roles (UKI 2, Nordics 1) are shown separately.
- **CSMs needed:** average monthly demand divided by effective hours (105 per CSM by default) at target utilisation, per book and per region, with the peak month. Renewal hours use 2027 term-end dates.
- **Decisions:** managed threshold 12,000 tARR; P3 and P4 renewals sit with the pool.
- **Result at defaults:** 4,711 MM/UM accounts; 1,642 managed and 3,069 pooled at 12,000 tARR. 40.8 managed and 11.8 pool CSMs are needed (52.7 in total), against 27 named ICs (gap -25.7), or 30 with open roles (gap -22.7).
- **Renewal hours (26 Nov):** 1 hour per managed renewal (MM and UM) and 30 minutes per pooled renewal, down from 5 and 10 hours managed and 1 and 1.5 hours pooled. Placeholders until the time study.
- **Data:** `scripts/build_inputs.py` now also emits bins, renewals and image tiers by segment and region, review headcount, and AM vs Vitally conflicts. The team population is unchanged (8,270 accounts).
- **Corrections:** the v3.2 status text and considerations have been rewritten for MM/UM only. Some v3.2 numbers no longer apply.
- **Leaders (26 Nov):** UKI is led by Tom Macbride. Stina Grahn is on maternity leave; Jakob Klöfver manages Nordics and owns a book. A leader-time input per region records management share, at 0 until set.
- **Known gaps:** hours and touch cadence are placeholders; tARR's definition is unconfirmed; the roster differs between the review and the chart; Nordics management time is not yet deducted; 148 MM/UM accounts sit with deactivated CSMs; Rest of World has 38 accounts and no named leader.

## v3.2 (prototype), 24 Nov 2026

Switches the account source to the Vitally tab and measures AM vs Vitally conflicts.

- **Population:** the Vitally tab (`nov18vitally raw data`) is now the source for account numbers. The team is the Vitally accounts whose CSM is on the roster (the CSM names in the accounts export). This gives 8,270 accounts, up from 7,813: 7,810 of the export's accounts plus 460 more. Three export accounts drop out.
- **Tiers:** from Vitally. The team has no blank tiers there (the export has 277), and tiers agree with the export on 84% of overlapping accounts. Managed P1/P2 is now 2,218 accounts (was 1,884).
- **ARR:** from Vitally, EUR 44.9m for the team (was EUR 42.6m).
- **AM conflicts:** a new table measures where AM and Vitally disagree. ARR differs by more than 1% on 569 accounts (EUR 0.6m combined). 3,315 team accounts are not in AM. Five owner records name different people. AM's "OTHER MARKETS" label is a taxonomy gap (185 accounts), not a conflict.
- **Builder:** `scripts/build_inputs.py` now takes the CX workbook, AM extract and accounts export (the export is used only for the roster). The CX population drives the aggregates.
- **Open:** the team roster (45 names, the brief says 30) needs confirming. Former-employee owners (159) need reassigning.

## v3.1 (prototype), 24 Nov 2026

Adds the 2027 company targets from the project brief and the P1/P2 managed-book and P3/P4 pool views.

- **2027 targets as inputs:** SLG EUR 5.5m, PLG EUR 12.6m, LARR EUR 18.2m. Read as expansion (SLG + PLG) and lost-ARR budget (LARR). Both readings are unconfirmed.
- **Top-down:** the company expansion rate (20.6%) and lost-ARR rate (20.7%) are applied to every team segment. Outputs are implied lost ARR, expansion ARR, accounts lost and expansion deals (at a EUR 12.8k placeholder deal size). The budget figures are shown next to them.
- **Managed book (P1/P2 only):** accounts per CSM at target, the optimal book (highest-ARR accounts first), the share of accounts and ARR it covers, and the cut-off ARR band.
- **Pool (P3/P4 and blank tiers):** accounts per pool CSM and pool utilisation against the 80% target.
- **Pooling assessment:** managed accounts below a chosen ARR band move to the pool. Outputs are accounts and ARR moved, CSM capacity freed and ARR at risk.
- **Monthly view:** accounts, demand, capacity, utilisation and CSM gap per book.
- **Fixes:** the monthly table header; utilisation now divides by average planned CSMs (it used month 12); the segment table shows ARR per book, not per segment.
- **Removed:** the annual gross churn and FY26 expansion placeholders. Churn and expansion now come from the 2027 targets.
- **CX example values relabelled:** the 70% focus, 33/66/100 ramp, SMB mix and buffer, SMB inflow and 57-account cap are marked ILLUSTRATIVE in the config, README and calculator. They show structure, not targets.
- **Still open:** bottom-up reactive volumes; renewal calendar by book (renewals are scaled pro rata by region); region-level CSM allocation; the FY27 headcount plan (the org deck shows vacancies, not a target).

## v3.0 (prototype), 23 Nov 2026

First version of the top-down and bottom-up calculator, shareable in the repo.

- Replaces the v2 two-book model with a single calculator that covers SMB, Mid Market, Upmarket and Onboarding.
- Top-down: monthly 2027 roll-forward of accounts and ARR by segment and book, using new accounts per month, annual gross churn and the FY26 expansion baseline.
- Bottom-up: hours per account-month by activity (touchpoints, at-risk, expansion, reactive, renewals, onboarding), with a buffer from the CX Capacity Model.
- Region filter, scaling accounts, renewals and planned CSMs pro rata.
- Revenue lens: ARR threshold for pooling managed accounts, CSM hours freed, ARR at risk.
- Data: team book aggregated from the accounts export (7,813 accounts), CX ARR and AM coverage. No account-level data in the repo.
- Editable profiles, headcount and growth inputs in the browser. Export scenario as JSON.

Known gaps in this version:
- Hours, touch cadence, hires, availability and pool churn are placeholders.
- No 2027 targets (the source shows TBD). FY26 baselines are used.
- Tier disagreement between the accounts export and the CX workbook is not resolved; the export is used.
- Former-employee owners are counted but not reassigned.

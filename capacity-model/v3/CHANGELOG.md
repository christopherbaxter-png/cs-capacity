# Changelog

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

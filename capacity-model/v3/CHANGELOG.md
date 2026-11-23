# Changelog

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

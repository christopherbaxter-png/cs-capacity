# CSM capacity calculator, v3 (prototype)

A single-page calculator for 2027 CSM capacity across SMB, Mid Market and Upmarket, with Onboarding as a separate population. It combines:

- **Top-down:** a monthly roll-forward of accounts and ARR for 2027, using new accounts per month, annual gross churn and the FY26 expansion baseline.
- **Bottom-up:** hours per account-month by activity (proactive touchpoints, at-risk, expansion, reactive, renewals, onboarding), sized from the CX Capacity Model and the project's v2 assumptions.
- **Revenue lens:** ARR in the managed and pool books, what moving low-ARR accounts to the pool frees up, and what ARR we accept at risk.

Open `index.html` in a browser. It has no dependencies and no server. Data is embedded, and nothing is sent anywhere.

## Status: read before using

- **Placeholders drive the result.** Hours per account, touch cadence, hires, availability and pool churn are placeholders (marked in `config/profiles.json`). Utilisation is illustrative until they are replaced.
- **The 2027 targets are not in the sources.** The Growth & Retention deck says "2027 Marketing Growth Target: TBD". The CX offsite shows the FY26 baselines (expansion EUR 17.7m, lost ARR EUR 18m) and the 2027 expansion target as `EUR Xm`. The model uses the FY26 baselines plus a growth input.
- **Current default result:** the managed book shows about 54 CSMs needed at target against 20 planned. The pool shows about 23 against 10. This comes from the placeholder touch cadence, not from calibrated data, so treat it as a starting point. Gong's recorded call time for the sample team is far lower (about 4 hours per CSM per month), so the hours-per-account inputs need calibrating before anyone relies on the gap.

## Files

| File | Purpose |
|---|---|
| `index.html` | The calculator. Generated; do not edit by hand. |
| `calculator.template.html` | Source for the calculator. Edit this, then rebuild. |
| `config/profiles.json` | Every default assumption, with its source or a PLACEHOLDER flag. |
| `data/team_book.json` | Aggregated team-book inputs. No account names, IDs or emails. |
| `scripts/build_inputs.py` | Builds `data/team_book.json` from the source exports. |
| `scripts/build_calculator.py` | Builds `index.html` from the template, config and data. |
| `CHANGELOG.md` | What changed in each revision. |

## Rebuild

```bash
cd capacity-model/v3
# 1. Re-aggregate from the source exports (run locally; the exports stay outside the repo)
python scripts/build_inputs.py ACCOUNTS.csv CX_PORTFOLIO.xlsx AM_PORTFOLIO.xlsx
# 2. Rebuild the calculator
python scripts/build_calculator.py
```

The v2 workbook and calculator in the parent folder are unchanged and kept for reference.

## How the model works

**1. Accounts and ARR (top-down).** For each segment and book (managed = P1/P2; pool = P3/P4 and blank tiers):

    accounts(m) = accounts(m-1) x (1 - annual churn / 12) + new accounts per month x book share

ARR follows the same roll-forward, with new accounts at the segment's average ARR and expansion allocated from the FY26 baseline by share of ARR.

**2. Demand (bottom-up).** Hours per account-month, by activity:

| Activity type | Hours per account-month |
|---|---|
| `share` | share of book active x hours per active account |
| `touchpoints` | touches per year / 12 x (hours per touch + extra hours per additional stakeholder) |
| `per_month` | hours per account-month |
| `per_year` | hours per account-year / 12 |
| `onboarding_total` | total hours / months in the onboarding window |

A buffer (15% for proactive books, from the CX model) is added. Renewals are added separately, as hours per renewal x renewals in that month from the 2027 Zuora calendar.

**3. Capacity.** Effective hours per CSM = contracted hours x portfolio share x availability (150 x 70% x 100% by default). Planned CSMs = starting CSMs + hires, with hires ramping 33% / 66% / 100% over three months.

**4. Outputs.** Utilisation against the target for each book (managed 85%, pool 80%), CSMs needed at target, and accounts per CSM at target. The CX model's cap of 57 is shown as a reference only; its source gives no derivation.

**5. Region.** Filtering by region scales accounts, renewals and planned CSMs by the region's share of the segment's accounts. A region therefore shows whether it is more or less loaded than average. It does not model the real regional CSM allocation, which the AM extract would need to confirm.

**6. Revenue.** Moving managed accounts below an ARR threshold to the pool frees CSM hours (difference between managed and pool hours per account, at the managed target). ARR at risk = ARR moved x placeholder churn uplift.

## Sources

| Input | Source |
|---|---|
| Team book (7,813 accounts, tiers, segments, country, renewals) | Accounts export (Vitally, current) |
| ARR | Nov 2026 CX portfolio review workbook, `vitally.custom.arrEur` |
| AM coverage (named CSM, former employees, market) | AM portfolio extract (`am_customer_extract`) |
| Hours, mix, ramp, focus, buffer, cap reference | CX Capacity Model (Account Caps), Hours tab |
| Contracted hours, targets, managed/pool split | Project instructions (v2) |
| FY26 expansion and lost ARR baselines | CX Strategy Offsite agenda, Nov 2026 |
| 2027 targets | Not available. Growth & Retention deck: "TBD" |

## Open decisions

1. Managed/pool split (20 and 10 is the starting point) and CSMs by segment.
2. Whether P3 and P4 renewals sit with the pool.
3. Tier source: the accounts export and the CX workbook disagree on tiers for 1,221 team accounts (84% agreement). The model uses the accounts export, which matches the project's counts.
4. Blank-tier accounts (277): pool by default.
5. Target utilisation for each book.
6. Which base to size against: the team book (7,813 accounts, 30 CSMs), or the CX model's 1,500-account SMB base.

## Considerations for the next revision

- **Calibration first.** A two-week time study by segment will replace most placeholder hours. Gong call data and email volumes per account (the `ask_account` sample) can cross-check it.
- **Reactive load.** It is currently a percentage buffer. Ticket, escalation and fraud volumes per account per month would make it bottom-up.
- **Availability.** Holidays, sickness, meetings and internal time are not modelled (100% by default). This is the largest structural gap against real capacity.
- **Attrition and ramp.** Attrition, backfill lag and the cost of ramp (not just the three-month curve) are not modelled.
- **Renewal workload.** Renewals are priced per renewal. Long contracts and auto-renewals may need a different treatment.
- **Churn by segment.** Company-level churn is used. The churn probability field in Vitally is empty in the current export.
- **Targets.** Plug in the 2027 expansion and churn targets once confirmed, and link the calculator's ARR path to them.
- **Governance.** Former-employee owners hold 130 matched accounts. Reassign them before the managed/pool split is decided.
- **Source model issues.** The CX model's workload excludes its own "Net Expansion Playbooks" line (740h per month). Its WIP tab labels a surplus as a gap. Both are noted in the calculator's considerations list.
- **Privacy.** `data/team_book.json` holds aggregates only. Keep account-level exports out of the repo.

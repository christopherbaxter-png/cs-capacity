# CSM capacity calculator, v3.1 (prototype)

A single-page calculator for 2027 CSM capacity across SMB, Mid Market and Upmarket, with Onboarding as a separate population. It combines:

- **Top-down:** a monthly roll-forward of accounts and ARR for 2027, using new accounts per month, annual gross churn and the FY26 expansion baseline.
- **Bottom-up:** hours per account-month by activity (proactive touchpoints, at-risk, expansion, reactive, renewals, onboarding). Some values are illustrated from the CX Capacity Model example and the project's v2 assumptions. They show structure, not targets.
- **Revenue lens:** ARR in the managed and pool books, what moving low-ARR accounts to the pool frees up, and what ARR we accept at risk.

Open `index.html` in a browser. It has no dependencies and no server. Data is embedded, and nothing is sent anywhere.

## Status: read before using

- **The CX Capacity Model is an example, not a spec.** Its values and structure show what a calculator can look like. Several inputs (marked ILLUSTRATIVE in `config/profiles.json`) come from it. They are not validated for this team and should be replaced with the team's own data.
- **Placeholders drive the result.** Hours per account, touch cadence, hires, availability and pool churn are placeholders (marked in `config/profiles.json`). Utilisation is illustrative until they are replaced.
- **The 2027 targets come from the project brief, not a finance source.** SLG EUR 5.5m, PLG EUR 12.6m and LARR EUR 18.2m are entered as inputs. The model reads expansion as SLG + PLG (EUR 18.1m) and the lost-ARR budget as LARR. Both readings need confirming. The Growth & Retention deck still says "2027 Marketing Growth Target: TBD".
- **Current default result (Mid Market + Upmarket, all regions):** managed utilisation about 190% on average (peak about 220%) against an 85% target, with 17 planned CSMs. Pool utilisation about 240% against 80%, with 4 planned CSMs. This comes from the placeholder touch cadence, not calibrated data. Gong's recorded call time for the sampled CSMs is far lower (about 4 hours per CSM per month), so the hours-per-account inputs need calibrating before anyone relies on the gap.

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

Churn and expansion are company rates, derived from the 2027 targets: lost ARR = LARR / company ARR (18.2 / 87.9 = 20.7%), and expansion = (SLG + PLG) / company ARR (18.1 / 87.9 = 20.6%). Both are applied monthly to each team segment's ARR. New accounts enter at the segment's average ARR. The budget figures shown in the calculator are the same rates applied to the scope's ARR, so the match between budget and implied figures is a drift check, not evidence the plan is achievable.

**2. Demand (bottom-up).** Hours per account-month, by activity:

| Activity type | Hours per account-month |
|---|---|
| `share` | share of book active x hours per active account |
| `touchpoints` | touches per year / 12 x (hours per touch + extra hours per additional stakeholder) |
| `per_month` | hours per account-month |
| `per_year` | hours per account-year / 12 |
| `onboarding_total` | total hours / months in the onboarding window |

A buffer (15% for proactive books, illustrative, from the CX example) is added. Renewals are added separately, as hours per renewal x renewals in that month from the 2027 Zuora calendar.

**3. Capacity.** Effective hours per CSM = contracted hours x portfolio share x availability (150 x 70% x 100% by default). Planned CSMs = starting CSMs + hires, with hires ramping 33% / 66% / 100% over three months.

**4. Outputs.** Utilisation against the target for each book (managed 85%, pool 80%), CSMs needed at target, and accounts per CSM at target. The CX model's cap of 57 is shown as a reference only; its source gives no derivation.

- **Managed book (P1/P2 only).** The optimal book is the planned managed CSMs (average) x accounts per CSM at target. Accounts are taken from the highest-ARR bands first, so the output shows which accounts the optimal book covers, the ARR share, and the cut-off band. ARR bands come from `managed_arr_bands` in the team book.
- **Pool (P3/P4 and blank tiers).** Accounts per pool CSM at the 80% target, and pool utilisation.
- **Pooling assessment.** Managed accounts up to a chosen ARR band move to the pool. The calculator reports accounts and ARR moved, CSM hours freed (managed minus pool hours per account, at the managed target), and ARR at risk (ARR moved x the pool churn placeholder).

**5. Region.** Filtering by region scales accounts, renewals and planned CSMs by the region's share of the segment's accounts. A region therefore shows whether it is more or less loaded than average. It does not model the real regional CSM allocation, which the AM extract would need to confirm.

**6. Revenue.** Moving managed accounts below an ARR threshold to the pool frees CSM hours (difference between managed and pool hours per account, at the managed target). ARR at risk = ARR moved x placeholder churn uplift.

## Sources

| Input | Source |
|---|---|
| Team book (7,813 accounts, tiers, segments, country, renewals) | Accounts export (Vitally, current) |
| ARR | Nov 2026 CX portfolio review workbook, `vitally.custom.arrEur` |
| AM coverage (named CSM, former employees, market) | AM portfolio extract (`am_customer_extract`) |
| Hours, mix, ramp, focus, buffer, cap reference | ILLUSTRATIVE. CX Capacity Model (Account Caps) example, Hours tab. Used to show structure; not validated for this team. |
| Contracted hours, targets, managed/pool split | Project instructions (v2) |
| FY26 expansion and lost ARR baselines | CX Strategy Offsite agenda, Nov 2026 |
| 2027 targets: SLG EUR 5.5m, PLG EUR 12.6m, LARR EUR 18.2m | Project brief, 24 Nov 2026. Interpreted (see Open decisions). |
| Company ARR base (EUR 87.9m) | CX offsite agenda, used for the 20.5% FY26 churn rate |
| Average expansion deal (EUR 12.8k placeholder) | CX Capacity Model WIP tab, ASP USD 12,000 to 12,800. Currency unconfirmed. |

## Open decisions

1. Managed/pool split (20 and 10 is the starting point) and CSMs by segment.
2. Whether P3 and P4 renewals sit with the pool.
3. Tier source: the accounts export and the CX workbook disagree on tiers for 1,221 team accounts (84% agreement). The model uses the accounts export, which matches the project's counts.
4. Blank-tier accounts (277): pool by default.
5. Target utilisation for each book.
6. Which base to size against: the team book (7,813 accounts, 30 CSMs), or the CX model's 1,500-account SMB base.
7. What SLG, PLG and LARR mean. The model reads expansion = SLG + PLG and lost-ARR budget = LARR. Confirm with Finance.
8. How the targets split by segment. PLG (EUR 12.6m) is larger than the team's whole SMB ARR (EUR 8.8m), so the targets cannot be allocated from the team book alone. The model applies them as company-wide rates.
9. The FY27 CSM headcount plan. The org deck ("CX Org planning - Oct 2026") shows vacancies and backfills marked "Decision pending" and no numeric target.
10. Which tier source is authoritative (accounts export or CX workbook), and whether former-employee accounts (130 matched) are reassigned.

## Considerations for the next revision

- **Calibration first.** A two-week time study by segment will replace most placeholder hours. Gong call data and email volumes per account (the `ask_account` sample) can cross-check it.
- **Reactive load.** It is currently a percentage buffer. Ticket, escalation and fraud volumes per account per month would make it bottom-up.
- **Availability.** Holidays, sickness, meetings and internal time are not modelled (100% by default). This is the largest structural gap against real capacity.
- **Attrition and ramp.** Attrition, backfill lag and the cost of ramp (not just the three-month curve) are not modelled.
- **Renewal workload.** Renewals are priced per renewal. Long contracts and auto-renewals may need a different treatment.
- **Churn by segment.** Company-level churn is used. The churn probability field in Vitally is empty in the current export.
- **Targets.** Confirm the meaning and segment split of SLG, PLG and LARR. Replace the company rates with segment-level rates once they are set.
- **Governance.** Former-employee owners hold 130 matched accounts. Reassign them before the managed/pool split is decided.
- **Example model issues.** The CX example's workload leaves out its own "Net Expansion Playbooks" line (740h per month). Its WIP tab labels a surplus as a gap. Both are noted in the calculator's considerations list, to check before reusing the example's structure.
- **Privacy.** `data/team_book.json` holds aggregates only. Keep account-level exports out of the repo.

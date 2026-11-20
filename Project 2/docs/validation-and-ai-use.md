AI announcement: I used OpenAI Codex to help build, test, and document the Project 2 app. I must independently review the evidence, checks, and decision; those judgments are mine.

Education, not investment advice: This is a FIN 43900 learning demonstration, not investment advice.

# Project 2 Validation and AI Use - Working Record

## Current run identity

- Repository: `439-work/Project 2/`; run from the repository root with
  `./.venv/bin/python -m streamlit run "Project 2/app.py"`.
- Data boundary: ten Nasdaq month-end `Close/Last` prices from January 31, 2024, through
  September 30, 2026; 32 monthly price changes. The separate classroom signal ends June 2026.
- [Price source and transform](../data/prices-source.md): source URL pattern, per-ticker raw
  checksums, CSV checksum, common-window check, and the unadjusted-price limitation.
- Ten-fund universe: VOO, VTI, VNQ, VWO, FBTC, FBND, FIVA, SGOV, TLT, TIP. All ten selected
  at startup; TLT and TIP can be removed or receive zero weight. Only SGOV is reserve eligible by default. The
  ten six-fund themes use this universe.
- Annual return inputs are editable **illustrative scenario assumptions** in `portfolio.py`.
  They are not calculated from the unadjusted price panel and are not verified forecasts.
- Working base: 9% scenario return target, 1% SGOV reserve floor, 30% price-drawdown review
  trigger, 40% general ticker cap, 10% FBTC cap, 60% broad-bucket cap, 70% high-correlation
  pair cap, 10% short cap, 110% gross cap, 25% annual one-way turnover limit, and 75%
  liquidity within 10 business days. Five-year horizon, quarterly review, annual core
  rebalance. These controls still require committee approval.

## Current validation status

| Required check | Evidence and result | Status |
|---|---|---|
| Known-answer mechanics | Lab 14 classroom engine remains; twelve Project 2 unit/AppTest checks pass locally on November 19 | Local pass |
| Ten-fund app and selected-fund limit | AppTest opens all ten selected funds with no exception/error | Local pass |
| Mandate finder | Exact fixed-weight boundaries for return, SGOV reserve, ticker, FBTC, short, gross, bucket, pair, and drawdown; a three-fund known-answer case checks the math | Local pass; student review pending |
| Numerical Auto-Pass | Finds the maximum scenario return under unchanged reserve/risk controls, applies weights and a rounded-down target, and restores prior inputs; a known-answer case checks the cap and reserve | Local pass; not a process PASS |
| Full-process pass check | Rechecks every displayed gate and lists actions for FAIL/REVIEW; test confirms failed holdout, turnover, and missing data are not relabeled | Local pass; adoption still blocked |
| Numerical base | At 9% target and 10% FBTC cap, default ten-fund search has `NO FEASIBLE MIX` under illustrative returns | Local result |
| Changed-control sensitivity | At 7.5% target, the app displays allocation `PASS` while full process stays `REJECT / REDESIGN`; this is an AI-assisted local check, **not** the required AI-off locked run | Local result |
| Estimation-window control | Bundled full 32-return and recent 24-return price-risk samples are selectable; a model test checks that volatility and correlations change | Local pass; price-only limitation remains |
| Data integrity | Month-end common panel checks and SHA lineage are recorded; Close/Last excludes cash distributions, and no verified total-return panel is supplied | REVIEW, adoption blocked |
| Overlap and concentration | VOO/VTI share a broad U.S. bucket; a correlation-pair screen is visible; FBTC has a separate 10% cap | Proxy screen only; holdings look-through pending |
| Reserve | SGOV is the only working reserve candidate; TLT never counts as cash | Issuer mandate checked; final committee eligibility/liquidity review pending |
| Point-in-time signal | One-month lag, selection ledger, zero-lag leakage diagnostic in [signal card](signal-data-card.md) | Classroom signal only |
| Holdout and costs | Frozen development 6.13% net; holdout -6.09% net versus -2.09% buy-and-hold; 400% development one-way turnover versus 25% limit | FAIL, adoption blocked |
| Partner cold run | Peyton's November 17 Windows run and first failure concern the earlier six-fund version; see [verbatim note](evidence/peyton-cold-run-rerun.md) | Retained as prior-version evidence; current ten-fund revision has no partner run |
| Locked Changed-Input Record | November 15 AI-off prediction and result exist, but the cited base SHA was not a pre-run commit | Incomplete; fresh human prediction and pre-run commit required |
| Checked AI output | The old TLT-reserve stress was qualified, then the new design removed TLT reserve eligibility | Human review of new data and mandate logic pending |

## Data and calculation boundaries

`data/prepare_nasdaq_monthly.py` takes the final common trading close each month and rejects
missing months, inconsistent dates, or nonpositive closes. The loader rejects unordered,
missing, and nonpositive prices; it does not impute. Volatility is monthly price-change sample
standard deviation times square root of 12. Correlations and historical drawdown are also
price-only. **Cash distributions are not included**, so the bundled series cannot validate
economic return for SGOV, FBND, TLT, TIP, VNQ, or the full portfolio. The default return
assumptions are scenario values chosen during app construction, not Luke's independent forecasts.
The app shows a return-data-quality REVIEW gate and must not describe a numerical PASS as an
adoptable portfolio.

The fixed-weight mandate finder computes mathematical boundaries for a chosen, 100%-total
weight vector. It does not search for a favorable policy or edit the working mandate. It
reports the largest return target and reserve floor the mix can meet, plus the smallest
permitted caps/tolerances. At the initial equal-weight ten-fund mix, the return ceiling is
6.45% and the FBTC weight is 10%, so the 9% target fails while the 10% FBTC cap passes. The other
numerical boundaries are shown in the app and in `outputs/visible-output.txt`. Even a
numerically compatible mix cannot clear the separate frozen holdout, turnover, data-quality,
issuer, liquidity, or derivative evidence by changing its mandate.

The Auto-Pass button searches only the selected funds. It maximizes scenario return on
the displayed weight grid, uses lower volatility to break return ties, and preserves the
current reserve, ticker, bitcoin, overlap, short/gross, and drawdown controls. If needed,
it lowers only the displayed return target to the nearest usable 0.1 percentage point.
The default ten-fund run finds 7.75% scenario return and applies a 7.7% target with
VOO 40%, VTI 20%, FBTC 10%, FIVA 20%, and SGOV 10%. The numerical allocation becomes
PASS, but the frozen process remains REJECT / REDESIGN. This sensitivity does not
approve changing the working 9% mandate or validate the return assumptions.
The adjacent full-process pass check reports each current FAIL and REVIEW with the
missing work. It does not alter gate statuses, thresholds, or the frozen holdout. A new
untouched test period and verified data cannot be generated by clicking a button.

The ten-theme audit uses the same scenario returns and constraints. Numerical allocation
results are scenario screens. Neither its favorable themes nor the short 2024-2026 price
window establish out-of-sample returns for the new ETF composition.

## Frozen classroom rule and decision

| Period | Gross | Net after 0.10% per switch | Buy-and-hold | Switches |
|---|---:|---:|---:|---:|
| Development | 6.55% | 6.13% | 5.33% | 4 |
| Holdout | -5.52% | -6.09% | -2.09% | 6 |

The monthly equity-versus-bills rule is separate from the ten-fund ETF composition. It uses
a one-month availability lag. Its zero-lag development net of 17.72% is a rejected leakage
diagnostic, not a candidate strategy. The failed holdout and 400% one-way development
turnover support `REJECT / REDESIGN`. The working mandate does not become suitable merely
because a lower return hurdle admits a numerical mix.

## Historical partner and changed-input records

Peyton's November 17 [note](evidence/peyton-cold-run-rerun.md) preserves the original Windows
README setup failure and AI-assisted continuation. Luke confirmed that Peyton later completed
the remaining partner tasks, but the supplied note does not document a separate post-fix
README-only rerun. The Windows README fix was published in commit `6782c19`. This evidence
applies to the prior six-fund version. It is not a cold run of the current ten-fund app.
Luke is using that earlier partner run as the available partner evidence. Local automated
checks and Luke's pending on-screen review cover the revised version, with this scope
distinction preserved for the grader.

Luke's November 15 [Lab 20 record](../../Post%20Project%201/Lab20/lab20_record.md) preserves
an AI-off prediction before changing the old objective from 9.00% to 10.50%, the observed
theme-pass decrease, and the unchanged reject/redesign decision. Its cited `44ee60e` SHA was
only the base HEAD while Project 2 was uncommitted. Commit `813865c` came after the run.
Neither proves a **pre-run committed prediction**. The historical result remains accurate,
but the Project 2 Locked Changed-Input Record is incomplete. Luke must write a new AI-off
prediction with units, expected direction, finance mechanism, and expected decision effect;
commit it before the run; then record exact before/after outputs, actual direction, decision
effect, and diagnosis. No assistant-authored prediction or retrospective timestamp will
stand in for that step.

## Locked Changed-Input Record - pending human AI-off entry

This test is reserved for Luke's independent prediction. The app baseline is frozen before
this section is filled. Do not use Auto-Pass while recording the test: it changes both the
return target and weights.

| Test setup | Frozen value |
|---|---|
| Price source and window | Bundled ten-fund CSV; full 32 monthly price changes |
| Fund selection | All ten funds selected |
| Scenario target and reserve minimum | 7.5% annual return; 1% SGOV reserve |
| Chosen weights, entered manually before the base observation | VOO 40%, VTI 20%, FBTC 10%, FIVA 20%, SGOV 10%; other five 0% |
| Single changed control | Maximum ticker weight: 40% to 30% |
| All other controls | Keep the app defaults, including the separate 10% FBTC cap |

**Before opening or running the changed case, Luke fills these lines with AI closed,
then commits and pushes this file:**

- AI-off prediction written at (date, time, time zone): [Luke fills in]
- Expected change in a named output (direction, rough size, and units): [Luke fills in]
- Finance reason for that direction: [Luke fills in]
- Expected effect on the numerical allocation verdict and full-process decision: [Luke fills in]
- Pre-run prediction commit SHA and GitHub link: [add after the prediction commit; do not amend it after the run]

**After the prediction commit is visible on GitHub and the base/changed cases are run:**

- Base output, with units and screenshot or visible-output evidence: [pending]
- Changed output, with units and screenshot or visible-output evidence: [pending]
- Actual direction and size versus prediction: [pending]
- Numerical and full-process decision effect: [pending]
- Mismatch diagnosis, or why the result did not change: [pending]

## Named AI-use register

| Tool/model | Date | Material use | Disposition |
|---|---|---|---|
| OpenAI Codex (exposed model ID not recorded) | October-November 2026 | Built Lab 15 engine and integrated earlier six-fund Project 2 app and classroom signal | Known-answer and local app checks passed; full process rejected on holdout and turnover |
| OpenAI Codex (exposed model ID not recorded) | November 15, 2026 | Suggested TLT reserve-eligibility stress | Qualified; the test showed classification mattered but did not prove TLT was cash |
| OpenAI Codex (exposed model ID not recorded) | November 17, 2026 | Helped repair Windows README and draft recording package after Peyton's note | Accepted supported setup fix; no independent post-fix log inferred |
| OpenAI Codex (exposed model ID not recorded) | November 19, 2026 | Helped replace the fund universe, prepare Nasdaq price-only panel, add FBTC cap and inverse mandate finder, and update tests/docs | Local nine-test and AppTest checks recorded; data-quality REVIEW and human validation remain open |
| OpenAI Codex (exposed model ID not recorded) | November 19, 2026 | Helped add numerical Auto-Pass, the full-process pass check, and the floating verdict layout | Local eleven-test and AppTest checks recorded; process and data gates remain open |
| OpenAI Codex (exposed model ID not recorded) | November 19, 2026 | Added a selectable 24-return estimation window and prepared an empty locked-input record | Twelve local tests passed; Luke's prediction and changed run remain pending |

## Freeze checklist

- [x] Ten-fund source panel and calculation boundary disclosed.
- [x] Current numerical base and full-process decision displayed together.
- [ ] Human-authored AI-off prediction committed **before** a new changed-input run.
- [x] Prior-version partner cold run retained with its scope disclosed; no current-version partner run claimed.
- [ ] Luke reviews the revised app and mandate finder on screen.
- [ ] Verified total-return history and independently justified return assumptions for an adoptable proposal.
- [ ] Revised recordings, corrected transcripts, stable links/durations, and final commit/access check.

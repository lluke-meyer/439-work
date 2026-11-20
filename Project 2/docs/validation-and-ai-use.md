AI announcement: I used OpenAI Codex to help build, test, and document this app. I take responsibility for the analysis, checks, and committee decision.

Education, not investment advice: This is a FIN 43900 learning demonstration, not investment advice.

# Project 2 Validation and AI Use

## Current run identity

- I keep the app in `439-work/Project 2/`; I run it from the repository root with
  `./.venv/bin/python -m streamlit run "Project 2/app.py"`.
- I use ten Nasdaq month-end `Close/Last` prices from January 31, 2024, through
  September 30, 2026; 32 monthly price changes. The separate classroom signal ends June 2026.
- I document source URLs, raw and CSV checksums, the common window, and the unadjusted-price
  limit in my [price-source record](../data/prices-source.md).
- I selected VOO, VTI, VNQ, VWO, FBTC, FBND, FIVA, SGOV, TLT, and TIP. All ten start
  selected, though any can receive zero weight. Only SGOV counts toward the reserve by
  default. My ten six-fund themes use this same universe.
- I treat annual returns in `portfolio.py` as editable **illustrative scenario assumptions**.
  They do not come from the unadjusted price panel and are not verified forecasts.
- My working base uses a 9% scenario return target, 1% SGOV reserve floor, 30% price-drawdown review
  trigger, 40% general ticker cap, 10% FBTC cap, 60% broad-bucket cap, 70% high-correlation
  pair cap, 10% short cap, 110% gross cap, 25% annual one-way turnover limit, and 75%
  liquidity within 10 business days. Five-year horizon, quarterly review, annual core
  rebalance. These are proposed limits; the committee has not approved them.

## Current validation status

I used Codex for these local checks. I demonstrate the revised app and explain the
post-run result in the three recordings linked from the [manifest](../recording-package/manifest.md).

| Required check | Evidence and result | Status |
|---|---|---|
| Known-answer mechanics | I kept the Lab 14 classroom engine; Codex ran twelve Project 2 unit/AppTest checks on November 19 | Local pass |
| Ten-fund app and selected-fund limit | I used AppTest to open all ten selected funds without an exception or error | Local pass |
| Mandate finder | I used a three-fund known answer to check return, reserve, ticker, FBTC, short, gross, overlap, and drawdown boundaries; I demonstrate it in Video 3 | Local pass |
| Numerical Auto-Pass | I used local tests to check unchanged risk limits, a usable target and weights, and restoration of prior inputs | Local pass; not a process PASS |
| Full-process pass check | I used a local test to confirm FAIL and REVIEW gates are not relabeled | Local pass; adoption blocked |
| Numerical base | At my 9% target and 10% FBTC cap, the ten-fund search shows `NO FEASIBLE MIX` under the scenario returns | Local result |
| Earlier control sensitivity | At 7.5% target, I observed allocation `PASS` and full-process `REJECT / REDESIGN`; this AI-assisted check was separate from my locked test | Local result |
| Estimation window | I can select all 32 or the latest 24 price returns; a model check confirms volatility and correlations change | Local pass; price-only data |
| Data integrity | I recorded the common panel and checksums, but Close/Last excludes cash distributions and I lack verified total returns | REVIEW, adoption blocked |
| Overlap and concentration | I group VOO/VTI exposure, screen correlated pairs, and cap FBTC at 10% | Proxy screen only; no holdings look-through |
| Reserve | I count SGOV as the working reserve and never count TLT as cash | Proposed policy; committee approval absent |
| Point-in-time signal | I use a one-month lag, a selection ledger, and the zero-lag check in my [signal card](signal-data-card.md) | Classroom signal only |
| Holdout and costs | I recorded 6.13% development net, -6.09% holdout net versus -2.09% buy-and-hold, and 400% turnover versus a 25% limit | FAIL, adoption blocked |
| Partner cold run | I retain Peyton's [November 17 note](evidence/peyton-cold-run-rerun.md) for the earlier six-fund version | No current ten-fund partner run |
| Locked Changed-Input Record | I pushed my AI-off prediction in `6055fcc` before the 40% to 30% cap run; [output](../outputs/locked-changed-input-output.txt) records both cases, and Video 1 explains the partial match | Pre-run lock and local run complete |
| Checked AI output | I challenged TLT reserve eligibility and removed it from the revised design; I identify FBTC's 12% scenario return and price-only data as unresolved assumptions | Adoption remains blocked |

## Data and calculation boundaries

I use `data/prepare_nasdaq_monthly.py` to take the final common trading close each month.
It rejects missing months, inconsistent dates, and nonpositive closes. The loader also
rejects unordered, missing, or nonpositive prices instead of filling gaps. I estimate
annualized price volatility from monthly sample standard deviation times the square root
of 12; correlation and drawdown are price-only too. **The panel excludes cash distributions.**
It cannot validate economic returns for SGOV, FBND, TLT, TIP, VNQ, or the whole portfolio.
The default return assumptions were chosen during app construction, not from my own
independent forecasts. I leave return data quality at REVIEW and do not treat a
numerical PASS as an adoptable portfolio.

I use the fixed-weight finder to ask what limits a chosen mix would need. The weights must
total 100%. It shows the highest return target and reserve floor the mix can meet, and
the minimum caps or tolerances it requires. It does not edit my working mandate. For
my starting equal-weight mix, the return ceiling is 6.45% and FBTC weighs 10%. The 9%
target fails while the FBTC cap passes. I show the other boundaries in the app and
`outputs/visible-output.txt`. A compatible mix cannot clear the separate holdout,
turnover, data-quality, liquidity, issuer, or derivative checks.

I use numerical Auto-Pass to search the selected funds on the displayed weight grid.
It maximizes scenario return, breaks ties with lower volatility, and keeps the reserve,
ticker, bitcoin, overlap, short/gross, and drawdown limits. If the return target is too
high, it lowers only that target to a usable tenth of a percentage point. With all ten
selected, it finds 7.75% scenario return and applies 7.7% with VOO 40%, VTI 20%,
FBTC 10%, FIVA 20%, and SGOV 10%. I can restore my prior inputs afterward. This makes
the numerical allocation PASS; the process stays REJECT / REDESIGN. I would not treat
that button as approval of a new 7.7% mandate or validation of the return assumptions.
The full-process button instead lists each FAIL and REVIEW and the evidence I would
need. It cannot change the frozen holdout, supply verified data, or approve policy.

I test ten starting themes under the same scenario returns and limits. A passing theme
is a numerical screen, not out-of-sample performance of the new ETF composition.

## Frozen classroom rule and decision

| Period | Gross | Net after 0.10% per switch | Buy-and-hold | Switches |
|---|---:|---:|---:|---:|
| Development | 6.55% | 6.13% | 5.33% | 4 |
| Holdout | -5.52% | -6.09% | -2.09% | 6 |

My monthly equity-versus-bills rule is separate from the ten-fund ETF mix. I keep a
one-month availability lag. Removing it raises development net to 17.72%, which I treat
as a leakage warning, not a candidate strategy. The failed holdout and 400% one-way
development turnover support my `REJECT / REDESIGN` decision. A lower return hurdle
does not fix those failures.

## Historical partner and changed-input records

I keep Peyton's November 17 [note](evidence/peyton-cold-run-rerun.md) because it records
the original Windows README setup failure and AI-assisted continuation. I confirmed
that Peyton later completed the remaining partner tasks, but his supplied note does
not show a separate post-fix README-only rerun. I published the Windows README fix
in `6782c19`. That cold run covers the earlier six-fund version, **not** this ten-fund
revision. I retain it with that limit stated. Videos 1 and 3 show my on-screen check
of the revised app.

My November 15 [Lab 20 record](../../Post%20Project%201/Lab20/lab20_record.md) preserves
an earlier AI-off prediction for a 9.00% to 10.50% objective change. Theme passes fell,
and the reject/redesign decision did not move. Its cited `44ee60e` was only the base
HEAD while Project 2 changes were uncommitted; `813865c` came after that run. I do not
use it as proof of a pre-run committed prediction. My November 19 test below has a
separate, pushed pre-run prediction. I kept my prediction wording intact; Codex helped
run the two cases and draft the comparison afterward.

## Locked Changed-Input Record - November 19, 2026

I froze the app baseline in [`a7eae6a`](https://github.com/lluke-meyer/439-work/commit/a7eae6a5d36dacc141ac45b367c09d0838b30a12)
and pushed my AI-off prediction in [`6055fcc`](https://github.com/lluke-meyer/439-work/commit/6055fcc6f75e4f33c915b5aca7234d65b7dd35e4)
at 8:00:52 PM EST, before the local run. I did not use Auto-Pass for this test because
it changes both the return target and weights.

| Test setup | Frozen value |
|---|---|
| Price source and window | Bundled ten-fund CSV; full 32 monthly price changes |
| Fund selection | All ten funds selected |
| Scenario target and reserve minimum | 7.5% annual return; 1% SGOV reserve |
| Chosen weights, entered manually before the base observation | VOO 40%, VTI 20%, FBTC 10%, FIVA 20%, SGOV 10%; other five 0% |
| Single changed control | Maximum ticker weight: 40% to 30% |
| All other controls | Keep the app defaults, including the separate 10% FBTC cap |

**My pre-run prediction, preserved as committed:**

- AI-off prediction written at (date, time, time zone): 11/19/2026, 8:00 PM EST
- Expected change in a named output (direction, rough size, and units): Decrease in annual return around 1% and/or fewer portfolios achieve "Pass" status
- Finance reason for that direction: Allows for more diversification in the portfolio. VOO was regularly weighted 40% in most portfolios and I want to see whether that remains true.
- Expected effect on the numerical allocation verdict and full-process decision: I believe the return will fall and fewer portfolios will reach "Pass" status.
- Pre-run prediction commit SHA and GitHub link: [`6055fcc6f75e4f33c915b5aca7234d65b7dd35e4`](https://github.com/lluke-meyer/439-work/commit/6055fcc6f75e4f33c915b5aca7234d65b7dd35e4)

**Observed after the prediction commit:**

- Base output: I had Codex capture the 40% cap case in local AppTest. My fixed mix passed. The constrained search passed at 7.55% scenario annual return, 11.00% annualized price volatility, and 10% SGOV reserve. Three of ten starting themes passed. The exact inputs and output are in the [locked-run file](../outputs/locked-changed-input-output.txt).
- Changed output: I had Codex lower only the general ticker cap to 30%. My unchanged fixed mix failed its ticker check and numerical mandate. The constrained search still passed at 7.55% scenario annual return, 11.04% annualized price volatility, and 10% SGOV reserve. One of ten themes passed.
- Direction and size: I was right that fewer themes would pass: three fell to one. I was wrong about the roughly 1% annual-return drop. The displayed constrained-search scenario return stayed at 7.55%, a 0.00-percentage-point change.
- Decision effect: my **fixed mix** flipped PASS to FAIL because it still held 40% VOO under a 30% ticker cap. The **constrained search** found another passing mix. Full process stayed `REJECT / REDESIGN`; frozen holdout net stayed -6.09%. My pre-run text did not state a separate full-process forecast.
- Why the return did not move: a tighter ticker cap restricts weights, but it does not lower the editable return assumptions. The search could shift weight on its 10% grid and keep the same rounded 7.55% scenario return, although estimated volatility rose 0.04 percentage points. Fewer ten-fund starting themes still qualified. Codex helped draft this post-run explanation; it does not change my locked prediction.

## Named AI-use register

| Tool/model | Date | Material use | Disposition |
|---|---|---|---|
| OpenAI Codex (model ID not recorded) | October-November 2026 | I used it to build the Lab 15 engine and earlier six-fund app and classroom signal | Local known-answer and app checks passed; I rejected the process on holdout and turnover |
| OpenAI Codex (model ID not recorded) | November 15, 2026 | I used it to challenge whether TLT should count as reserve | I removed TLT reserve eligibility; the test did not prove it was cash |
| OpenAI Codex (model ID not recorded) | November 17, 2026 | I used it to fix the Windows README and prepare recording drafts after Peyton's note | I preserve the initial failure and do not claim a separate post-fix partner rerun |
| OpenAI Codex (model ID not recorded) | November 19, 2026 | I used it to build the ten-fund panel, FBTC cap, mandate finder, Auto-Pass controls, and verdict layout | Local checks passed; price and policy limits still block adoption |
| OpenAI Codex (model ID not recorded) | November 19, 2026 | I used it to add a 24-return window and prepare a blank locked-input record | Twelve local tests passed before I wrote my prediction |
| OpenAI Codex (model ID not recorded) | November 19, 2026 | I used it to run the two locked-input cases in local AppTest and draft the post-run comparison | My prediction stayed locked in `6055fcc`; the result partly matched and the process still failed |

## Freeze checklist

- [x] I disclosed the ten-fund price source and calculation limits.
- [x] I show the numerical allocation and full-process verdicts together.
- [x] I committed my AI-off prediction in `6055fcc` before the changed-input run and recorded both local outputs.
- [x] I retained Peyton's earlier cold run with its six-fund scope stated.
- [x] I show the app and mandate finder on screen and explain the post-run result in the recordings.
- [x] I state that verified total-return history and defensible return assumptions are absent; adoption remains blocked.
- [x] I recorded three videos, saved corrected transcripts, and linked their titles, durations, and evidence moments in the manifest.

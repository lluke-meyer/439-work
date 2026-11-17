AI announcement: I used OpenAI Codex to help organize the Project 2 application, calculations, and documentation. I independently review the evidence, checks, and recommendation; the analysis and decision remain mine.

Education, not investment advice: This is a FIN 43900 course project and learning demonstration, not investment advice.

# Project 2 Validation and AI Use - Working Record

## Run identity

- Working repository: `439-work`
- Working path: `Project 2/`
- Current prototype command: `.venv/bin/python -m streamlit run app.py`
- Current evidence boundary: bundled monthly adjusted-close prices through September 1, 2026;
  classroom signal data through June 2026.
- Optional live source: Yahoo Finance public chart endpoint, cached for one hour; record the
  retrieval date, lookback, source status, and fallback status before treating live output as evidence.
- User flow: decision-first hero, data source, six-fund theme, 3-10 fund count, editable
  assumptions, mandate gate, overlap audit, allocation results, baselines, and holdout evidence.
- Working mandate: 9% estimated return target before trading costs, 1% reserve floor, 30% drawdown review trigger,
  75% liquidity within 10 business days, 25% annual one-way turnover limit, 40% maximum long ticker
  weight, 10% maximum short ticker weight, 110% gross-exposure ceiling, 60% broad-exposure overlap
  cap, and 70% high-correlation pair cap. Derivatives are permitted for hedging but not priced in
  this app.
- The 30% drawdown trigger is the post-Lab-20 mandate revision for the requested moderately risky/risky
  posture. The historical 10.50% changed-input run remains recorded under its original 25% trigger.
- Final frozen commit: not created; final mandate, recordings, and publication remain open.

## Validation status

| Required check | Current evidence | Status |
|---|---|---|
| Known-answer/manual baselines | Lab 14 baseline and Lab 15 engine checks | Complete for classroom inputs; integrate into final app |
| Constraint and unit checks | Portfolio engine validates bounded net weights, gross exposure, covariance dimensions, correlations, bounds, ticker selection, and overlap buckets | Complete for current engine; holdings-level issuer and liquidity evidence pending |
| Point-in-time and revision audit | Labs 16-17 provenance funnel and the linked Project 2 signal data card | Complete for the frozen classroom signal; the input is course-authored rather than a live production feed |
| Naive benchmark and true holdout | Lab 18 classroom rule versus buy-and-hold, now visible in the Project 2 app | Complete for the frozen classroom rule |
| Costs and stress run | Switch cost in the backtest; bounded lag/cost controls and TLT/SGOV reserve-flag stress in the app | Complete for the frozen rule; observed reserve history remains a review item |
| Placebo/falsification test | Visible zero-lag leakage diagnostic; the one-month lag remains frozen | Complete as a falsification check, not a separate placebo |
| Cold run and visible output | Peyton's November 17 README-only Windows pass stopped at `python3 -m venv .venv`; an AI-assisted PowerShell continuation reached the decision and changed a control. See the [verbatim partner note](evidence/peyton-cold-run-rerun.md). | First failure documented and Windows README instructions added; clean post-fix rerun pending |
| Highest-risk counterexample | Removing both reserve candidates produces no feasible mix under the 1% floor | App gate shows reject/redesign; TLT remains a provisional proxy and SGOV is preferred |
| Ten-theme allocation audit | One of ten bundled-data themes produces an allocation-feasible mix under the bounded short/gross policy; the full process gate still rejects/redesigns | Complete as an allocation screen; process-level evidence remains unresolved |
| Locked Changed-Input Record | Scenario recorded in `Post Project 1/Lab20/lab20_record.md`; its cited SHA is the base HEAD while Project 2 was uncommitted | Pre-run GitHub lock not established by that SHA |
| Independent AI-output check | The reserve-eligibility test was run and its limitation identified | Complete for this working record; the result was qualified rather than accepted as proof that TLT is cash |

## Data and transformation record

- Price input: `prices.csv`, monthly adjusted close, common window October 2021 through
  September 2026.
- Fund universe: six observed default funds, with optional modeled SGOV, BND, VOO, and TIP candidates.
  A real uploaded history or live Yahoo history takes precedence over a modeled candidate.
- Return transformation: monthly price changes, annualized expected return as monthly mean times
  12, annualized volatility as monthly sample standard deviation times square root of 12.
- Portfolio search: bounded net weights on a ten-percentage-point grid under the default short and
  gross-exposure policy; feasible portfolios must meet the objective return, reserve minimum, ticker
  caps, gross-exposure ceiling, and overlap caps.
- Overlap test: gross broad exposure buckets plus a pairwise high-correlation screen, not holdings-level
  security overlap. U.S. equity beta currently groups VTI, SOXX, FREL, and VOO; pairs at or above
  70% estimated correlation have a 70% combined-weight cap by default. Derivatives are disclosed
  as hedge-permitted but remain outside the price-only allocation engine.
- Signal timing: the frozen classroom rule uses a one-month lag so the signal must be available
  before the position is selected.
- Signal data card and selection ledger: [`docs/signal-data-card.md`](signal-data-card.md) records the
  event/availability boundary, threshold, universe, lag, cost, holdout, and zero-lag diagnostic.
- Cost treatment: the classroom backtest subtracts a 0.10% switch cost whenever the position
  changes.
- Revision treatment: observations published after the decision date are excluded from the
  point-in-time panel; later revisions are retained as a separate audit question.

## Current validation results

The classroom holdout reproduced the known-answer result:

| Period | Rule gross | Rule net | Buy-and-hold | Decision |
|---|---:|---:|---:|---|
| Development | 6.55% | 6.13% | 5.33% | Development success |
| Holdout | -5.52% | -6.09% | -2.09% | Failure rule triggered |

Under the final controls, the default six-fund run provisionally allows TLT as the reserve proxy.
The constrained search produces 20% TLT, 10% SOXX, 30% VTI, and 40% VXUS, with a 9.19% estimated
return and 15.45% estimated volatility. The high-correlation VTI/VXUS pair is capped at a 70%
combined weight. The bounded short/gross controls are available, but this default result does not
need a short position. That is a sensitivity scenario, not proof that TLT qualifies as the $1 million
reserve.

## Partner cold-run evidence - November 17, 2026

Peyton's [completed note](evidence/peyton-cold-run-rerun.md) records a fresh ZIP of commit
`813865ced5ca2e38ec33cebf0086d713ea79ce00`. On Windows PowerShell, the README-only first
pass stopped after about 40 seconds at `python3 -m venv .venv`: `python3` resolved to the
WindowsApps alias, and the README supplied only Bash commands. The subsequent run used Windows
commands with Codex assistance. It reached the decision after approximately 6 minutes 23 seconds
from README review; that time includes installation, tool delays, and browser assistance.

In the assisted continuation, the default 9% objective showed allocation `PASS`, full process
`REJECT / REDESIGN`, and 9.19% estimated return. Raising the objective to 10% kept the two
verdicts, with 10.18% estimated return. Frozen holdout net remained -6.09% against -2.09%
buy-and-hold. Peyton's Windows test run reported eight passing tests and no app exception. The
full-process metric text was truncated at the tested window widths, although the full verdict
remained readable elsewhere on the page.
Luke confirmed that he explained `expected_portfolio_return` to Peyton without AI; Peyton's
note records the asset-alignment question and answer.

The README now includes the Windows commands that worked in the assisted continuation, published
in [commit `6782c19`](https://github.com/lluke-meyer/439-work/commit/6782c19c06301cf579d76198e184a55dc1057742). There has
not yet been a clean, independent README-only rerun after that fix. Peyton's code question also
identified that `expected_portfolio_return` checks vector lengths but relies on the caller to
keep asset order aligned; no wrong-order result was observed.

## Final decision

The selected allocation passes the displayed portfolio mandate. The full process remains
`REJECT / REDESIGN` - do not adopt or fund a live pilot while turnover, frozen holdout, reserve,
liquidity, issuer, point-in-time, or derivative-governance evidence remains open. Reverse the
decision only after those checks pass, the partner cold run is complete, and the final recording
and repository commit are frozen.

## Locked Changed-Input Record

The bundled-data Lab 20 scenario records a prediction before the objective-return change and the
actual result afterward. Its cited commit is the base HEAD while Project 2 was uncommitted, so it
does not by itself establish the required pre-run GitHub lock:

- Input changed: Objective Return
- Units: Annual percentage
- Old value: 9.00%
- New value: 10.50%
- Prediction timestamp: 11/15/2026 @ 6:45 PM
- Base commit at the time, not a committed Project 2 prediction: 44ee60ecada51f6751c5d4490a68463f6ebb2431
- Expected output direction: Down
- Expected decision effect: Fewer portfolios will achieve "Pass" status
- Actual output direction: Down
- Actual decision effect: Fewer portfolios achieved "Pass" status. Zero "themed" portfolios achieved "Pass" status.
- Matched or diverged: Matched
- Failure diagnosis or reason for no change: Raising the objective to 10.50% made the allocation screen stricter. The default six-fund result still passed the return gate at 10.68%, but all ten theme portfolios returned `NO FEASIBLE MIX` under the reserve, ticker-weight, overlap, bounded-exposure, and allocation-step constraints. The full process gate remained `REJECT / REDESIGN` because the drawdown, turnover, and frozen holdout checks still failed.

The original frozen rule and holdout remain locked evidence. A changed lag, cost, or estimate is a
sensitivity scenario, not permission to retune the holdout.

## Named AI-use register - working draft

| Tool/model | Interaction date | Material use | Independent disposition |
|---|---|---|---|
| OpenAI Codex (model identifier not exposed in the repository) | November 15, 2026 | Organized the Project 2 documentation, reviewed course instructions, and proposed the reserve-eligibility stress test | Qualified: the test supports that reserve classification is load-bearing, but does not prove TLT is cash-equivalent |

Before submission, add every material AI interaction, the exposed tool/model/version, the date,
the output considered, and whether it was accepted, qualified, corrected, or rejected.

## Reproducibility and access checklist

- [x] README contains a one-command local run for the current prototype.
- [x] Visible output is available through the Streamlit app and Lab 15 record.
- [x] Final app shows baselines, mandate verdicts, frozen holdout gross/net, bounded controls, and the leakage diagnostic.
- [ ] Partner can run the repository from the README alone after the Windows instructions are published and rerun.
- [ ] Final visible output, memo, and videos use the same numbers and dates.
- [x] No passwords, API keys, tokens, credentials, or private data are committed.

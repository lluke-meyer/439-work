# Lab 13 — Meridian Foundation Mandate Record

## Integrity note

This is an AI-assisted reconstruction created on Oct. 20, 2026 after the student missed Lab 13.
It does not claim that the required human-first work occurred without AI. The student must review
the record, make the final disposition, and retain the disclosure. The case is course practice and
must not be merged with the student's own Project 2 proposal.

## Decision contract

- Decision user: Meridian Foundation investment committee, advised by the CIO.
- Action: authorize further analysis and a small pilot, or defer; no trades are authorized.
- Investable universe: diversified public long-only exposures that can be tested against the
  policy constraints. No specific securities are authorized by the case.
- As-of boundary: Oct. 15, 2026 CIO facts. Lab 14 teaching inputs have an Oct. 20, 2026 course
  release and do not describe real securities.
- Policy objective: CPI + 4% net of estimated costs over rolling five-year periods.
- Optimization objective: unresolved; the committee has not chosen the measurable tradeoff.
- Horizon and review: seven years, quarterly review, annual rebalancing.
- Benchmark: 60% broad global equities / 40% U.S. investment-grade bonds.
- Risk: the 10% calendar-year-loss statement is non-operational until the CIO defines the
  measure, acceptable probability, and breach response.
- Naive baselines: 60/40 policy benchmark, equal weight, and inverse volatility.
- Current decision: `DEFERRED_NO_ADOPTABLE_CANDIDATE`. A clearly labeled mechanics-only classroom
  allocation may be calculated for Lab 14, but it cannot support adoption.

## Reconstructed statement classification

| CIO statement | Classification | Reason and operational treatment |
|---|---|---|
| Committee decides whether to authorize analysis and a small pilot, not trades | Hard decision boundary | No output may be represented as trade authorization. |
| Seven-year horizon; quarterly review; annual rebalancing | Hard policy constraint | Preserve all three in modeling and monitoring. |
| CPI + 4% net of estimated costs over rolling five-year periods | Objective | It is explicitly an objective, not a guaranteed outcome. |
| $750,000 distribution at each calendar quarter-end | Hard cash-flow fact | Annual scheduled distributions equal $3,000,000. |
| Twelve months of distributions in cash or daily-liquid government securities | Hard liquidity constraint | Maintain at least $3,000,000, or 3% of the current reserve, in eligible assets. |
| 60% global equity / 40% U.S. investment-grade bond policy benchmark | Hard evaluation reference | Compare against it; do not silently impose it as the portfolio's required weights. |
| Long-only; no borrowing, short sales, or derivatives | Hard constraints | Encode explicitly and audit. |
| Single issuer no more than 8% | Hard constraint | Requires issuer-level holdings data; broad sleeve weights alone cannot prove compliance. |
| Turnover should not exceed 25% absent documented exception | Hard default with exception path | Measure annual turnover; any breach needs committee approval and documentation. |
| At least 90% redeemable within five business days | Hard liquidity constraint | Requires security-level or vehicle-level liquidity evidence. |
| “Cannot have a calendar-year loss greater than 10%” | Unverifiable promise / aspiration requiring escalation | No risky portfolio can guarantee it; the measure, probability, and breach response are missing. |
| No sector, climate, social, tax, active, or home-bias preference supplied | Missing fact, not permission | Do not invent any of these preferences. |
| Pilot objective not defined | Requires clarification | Different defensible objectives can produce materially different allocations. |

## Evidence table

| Mandate element | Operational value | Governing fact | Ambiguity / escalation |
|---|---|---|---|
| Objective / benchmark | CPI + 4% net over rolling five years; compare with 60/40 | Stated objective and policy benchmark | CIO must choose the pilot's measurable optimization tradeoff and success threshold. |
| Horizon / rebalancing | 7 years; quarterly review; annual rebalance | Explicit dated facts | Define whether an exception allows interim rebalance after a breach. |
| Risk / loss tolerance | Track calendar-year return plus provisional volatility, drawdown, and shortfall measures | CIO's 10% loss statement | Define measure, probability, enforcement, and breach response. |
| Liquidity / turnover | $3m eligible liquid reserve; >=90% within five days; <=25% annual turnover by default | Distribution, liquidity, and turnover facts | Specify eligible vehicles, measurement convention, costs, and exception process. |
| Leverage / shorting / concentration / suitability | Long-only; no borrowing, shorts, or derivatives; issuer <=8%; no unstated preferences | Explicit constraints and stated preference gaps | Need issuer-level look-through and any later suitability instructions. |

## Missing facts that stop adoption

1. The governing optimization objective and success threshold.
2. The operational definition of the 10% calendar-year loss statement.
3. Inflation, expected-return, covariance, and cost estimation methods.
4. Security/vehicle-level issuer and liquidity classifications.
5. Starting holdings and tax lots, needed to measure turnover and implementation cost.
6. Any approved sector, ESG/climate, tax, active, or home-bias preference.

## Precommitted validation plan

1. Reconcile all inputs, units, labels, covariance cells, and portfolio arithmetic.
2. Compare the candidate with 60/40, equal-weight, and inverse-volatility baselines.
3. Audit every hard constraint and separately list constraints the supplied data cannot prove.
4. Prestate expected direction before perturbing means, covariance/correlation, and one bound.
5. If historical data are introduced later, freeze a dated out-of-sample window before fitting;
   Lab 14's synthetic point-in-time inputs have no holdout sample.
6. Deduct estimated costs and test the 25% turnover default.
7. Stress distribution coverage, liquidity, loss, and correlation behavior.
8. Fail adoption if a hard constraint fails, the recommendation is unstable, or the objective
   remains unresolved.

## Codex material-claim dispositions

| Claim | Tag | Governing fact / reason | Disposition |
|---|---|---|---|
| There are at least two defensible objectives that can change allocation | `supported` | The committee explicitly did not select expected return, tracking error, drawdown, distribution probability, or another tradeoff. | Accept as proof that optimization should pause. |
| The eligible twelve-month reserve is $3,000,000 | `supported` | Four quarter-end payments x $750,000. | Accept; arithmetic independently reproducible. |
| CPI + 4% should be treated as a probability target | `requires clarification` | The return objective is stated, but no probability standard is supplied. | Do not encode until CIO responds. |
| A tracking-error limit should be imposed | `unsupported` | A benchmark is supplied, but no tracking-error tolerance exists. | Reject as a hard rule; it may be a proposed interpretation only. |
| The 10% statement can be guaranteed by optimization | `unsupported` | No enforcement rule, probability, or unavoidable-breach response is supplied. | Reject. |
| Loss-risk control should take priority over CPI + 4% | `requires clarification` | Priority among objectives is not supplied. | Escalate. |
| All explicit long-only, leverage, liquidity, issuer, and turnover rules remain in either interpretation | `supported` | Each is stated directly in the case. | Accept and audit. |
| Security-level compliance can be proven from four broad asset sleeves | `unsupported` | Issuer and liquidity look-through data are absent. | Reject; label evidence limit. |

## Minimum question / action before optimization

Ask the CIO:

> Which measurable tradeoff should govern the pilot—probability of achieving CPI + 4% net of
> costs, benchmark-relative risk, downside/calendar-year loss risk, probability of meeting
> distributions, or another objective—and what measure, acceptable probability, and response rule
> define the 10% calendar-year loss statement?

Until answered, preserve `DEFERRED_NO_ADOPTABLE_CANDIDATE`. Lab 14 may use an explicitly provisional
mechanics objective, but the result cannot support committee adoption.

## Student final disposition

- Review completed by:
- Date/time:
- Codex mandate: `accept` / `modify` / `reject` / `unresolved`
- Reason in the student's own words:
- Final escalation question retained or revised:



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

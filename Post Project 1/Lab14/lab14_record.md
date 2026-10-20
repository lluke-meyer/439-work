# Lab 14 — Portfolio Construction and Stability Record

Run from the FIN 439 folder:

```bash
"Project 1/.venv/bin/python" "Post Project 1/Lab14/portfolio_starter.py"
```

The script calculates all three portfolios, verifies the two known covariance answers, and stops
with an error if any supported mechanical check fails.

## Mandate and decision boundary

- Decision user: Meridian Foundation investment committee, advised by the CIO.
- Decision: whether to authorize analysis and a small pilot, not whether to execute trades.
- Policy objective: CPI + 4% net of estimated costs over rolling five-year periods.
- Policy benchmark: 60% broad global equities / 40% U.S. investment-grade bonds.
- Horizon: seven years, quarterly review, annual rebalancing.
- Current decision: `DEFERRED_NO_ADOPTABLE_CANDIDATE`.
- Provisional classroom objective: minimize annualized variance subject to long-only weights that
  sum to one. This choice tests mechanics and does not resolve the CIO's missing preference.

## Input conventions

- Provenance: `COURSE_SYNTHETIC_TEACHING_INPUTS`.
- Sample boundary: `not applicable — no observed sample`.
- Evidence vintage: Oct. 20, 2026 course release.
- Frequency: annualized expected returns, volatilities, and covariance.
- Missingness: none in the supplied tables.
- Expected returns: course teaching inputs, not forecasts inferred from market history.

## Known-answer reconciliation

- Equal-weight known answer: four weights of `25.00%`.
- Variance cell: `GovBond = 0.06 x 1.00 x 0.06 = 0.003600`.
- Covariance cell: `USEquity, IntlEquity = 0.18 x 0.75 x 0.20 = 0.027000`.
- Correlation matrix labels match the statistics table, is symmetric, and has a unit diagonal.
- Covariance eigenvalues are nonnegative; minimum eigenvalue is approximately `0.002692`.

## Baselines and mechanics candidate

| Portfolio | GovBond | CorpBond | USEquity | IntlEquity | Expected return | Volatility | Constraint status |
|---|---:|---:|---:|---:|---:|---:|---|
| Equal weight | 25.00% | 25.00% | 25.00% | 25.00% | 6.500% | 9.805% | Testable weight checks pass; security-level checks unavailable |
| Inverse volatility | 43.48% | 28.99% | 14.49% | 13.04% | 5.609% | 6.803% | Testable weight checks pass; security-level checks unavailable |
| Minimum-variance mechanics candidate | 76.88% | 12.99% | 8.85% | 1.29% | 4.644% | 5.394% | Testable weight checks pass; not adoptable |

The candidate reduces annualized volatility by approximately `4.411` percentage points versus
equal weight and `1.409` percentage points versus inverse volatility. Its expected return is also
lower. That tradeoff illustrates why the CIO must choose the governing objective.

The 60/40 policy benchmark is named but not calculated from these tables because the data do not
define how `GovBond` and `CorpBond` map into the U.S. investment-grade bond sleeve or how the two
equity sleeves map into broad global equity. A proxy would require an invented composition rule.

## Mechanical checks

| Check | Result | Evidence |
|---|---|---|
| Labels and order | PASS | Statistics and correlation assets match exactly |
| Correlation symmetry and unit diagonal | PASS | Direct matrix checks |
| Covariance diagonal | PASS | Equals squared supplied volatilities |
| Positive semidefinite covariance | PASS | Minimum eigenvalue approximately 0.002692 |
| Candidate sums to one | PASS | Difference from 1.0 within 1e-10 |
| Long-only | PASS | Minimum weight 1.29% |
| No leverage | PASS | Gross exposure equals 100% |
| Finite outputs | PASS | All candidate weights and metrics are finite |

## Checks unavailable from supplied data

| Mandate requirement | Status | Missing evidence |
|---|---|---|
| At least $3,000,000 in cash or daily-liquid government securities | Unavailable | Asset eligibility and daily-liquidity classification |
| At least 90% redeemable within five business days | Unavailable | Security or vehicle liquidity data |
| Single issuer no more than 8% | Unavailable | Holdings and issuer look-through |
| Annual turnover no more than 25% by default | Unavailable | Starting weights and trade list |
| Net-of-cost result | Unavailable | Turnover and cost assumptions |
| No calendar-year loss greater than 10% | Unresolved | Measure, probability, scenario evidence, and breach response |

Unavailable checks are not treated as zero breaches or as passing results.

## Final decision

Reject adoption of the calculated weights. Retain them only as a reproducible classroom mechanics
example. Analysis can resume after the CIO selects the measurable objective and operational loss
rule, and after eligible-asset, issuer, liquidity, holdings, and cost data are supplied.

Exact CIO question:

> Which measurable tradeoff should govern the pilot—probability of achieving CPI + 4% net of
> costs, benchmark-relative risk, downside/calendar-year loss risk, probability of meeting
> distributions, or another objective—and what measure, acceptable probability, and response rule
> define the 10% calendar-year loss statement?

## Chat/Codex disclosure

Chat/Codex implemented and checked the supplied starter using only the course-authored inputs.
Accepted contributions were the covariance build, transparent baselines, and solver-free
long-only minimum-variance calculation. The candidate was modified to remain mechanics-only.
Claims that the supplied sleeves prove liquidity, issuer, turnover, cost, or loss-rule compliance
were rejected. No external market data or real securities were used.

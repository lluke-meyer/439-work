AI announcement: I used OpenAI Codex to help organize the Project 2 application, calculations, and documentation. I independently review the evidence, checks, and recommendation; the analysis and decision remain mine.

Education, not investment advice: This is a FIN 43900 course project and learning demonstration, not investment advice.

# Project 2 Decision Memo - Working Draft

## Decision and committee ask

**Final working recommendation: reject/redesign.** Do not adopt or fund a live pilot until the
reserve definition, mandate controls, costs, point-in-time signal checks, drawdown, turnover, and
holdout evidence pass. Do not treat TLT as a cash equivalent or the current classroom signal as a
verified investment process.

The committee should approve the process only if:

1. the chosen portfolio satisfies every hard mandate constraint;
2. the reserve asset is genuinely eligible and liquid for the required horizon;
3. the frozen signal survives the untouched holdout after costs; and
4. the changed-input stress does not materially reverse the decision without a documented response.

## Intended user and decision

The intended user is a portfolio or quantitative analyst advising an investment committee. The
system compares transparent allocation baselines with a constrained portfolio process and reports
an action range with monitoring triggers. The committee decision is whether to pilot, adopt,
rebalance, or reject the process under the final mandate.

## Evidence and as-of boundary

The current bundled universe contains six funds with monthly adjusted-close observations from
October 2021 through September 2026. The app keeps those six as the default, offers 3-10 fund
scenarios, and provides ten six-fund starting themes. SGOV, BND, VOO, and TIP are modeled
candidates unless the user uploads a price file or selects Yahoo Finance live mode. The working
mandate uses:

| Control | Working value |
|---|---:|
| Estimated annual return target | 9% before trading costs |
| Reserve floor | 1% of assets, or $1 million on a $100 million portfolio |
| Drawdown review trigger | 30%; review or pause, not automatic liquidation |
| Liquidity floor | 75% within 10 business days |
| Annual one-way turnover limit | 25% |
| Maximum ticker weight | 40% |
| Maximum broad-exposure overlap | 60% |
| Maximum high-correlation pair weight | 70% when estimated correlation is at least 70% |

These are historical model estimates, not forecasts. The process minimizes volatility subject to
the 9% estimated-return target. TLT is provisionally reserve eligible for this model, but iShares reports that TLT
holds 20-plus-year Treasury exposure with effective duration around 15 years, which makes it
liquid but materially sensitive to interest-rate changes. A short Treasury bill fund such as SGOV
is a cleaner reserve candidate; TLT should not be treated as cash without qualification. SGOV is
available in the app and receives the preferred reserve classification when selected, but it needs
an observed price file before its historical risk evidence is complete.

The classroom signal test is also informative but is not yet the final integrated Project 2
strategy. Its development net return was 6.13% versus 5.33% for buy-and-hold; its untouched
holdout net return was -6.09% versus -2.09% for buy-and-hold. That result triggers the frozen
failure rule and supports caution rather than adoption.

## Mandate, assumptions, and sensitivity

The working mandate permits bounded shorting up to 10% per ticker and gross exposure up to 110%.
The portfolio remains ETF-based and long-biased, with no unrestricted leverage. Derivatives are
permitted for hedging only, but the app does not price derivative contracts or model margin, Greeks,
financing spreads, or counterparty exposure; any derivative implementation requires a separate
contract-level risk review. The 8% issuer-concentration rule remains a holdings-level requirement,
not a ticker-weight shortcut. The app's 60% gross broad-bucket overlap test and 70% high-correlation pair
test are screening proxies; neither replaces holdings-level look-through.

The most consequential sensitivities are the reserve classification, historical drawdown, signal
turnover, and holdout result. TLT can satisfy the mathematical reserve floor in the working model,
but its reserve status remains a review item because its duration creates price risk.

The app also audits ten six-fund starting themes. Under the bundled source estimates, one of ten
starting themes produces an allocation-feasible mix. That does not change the overall pilot/reject
call because the process-level holdout, turnover, liquidity, issuer, and point-in-time checks still apply.

## Risks, failure conditions, and monitoring

| Risk or failure condition | Monitor | Reversal trigger |
|---|---|---|
| Reserve asset is not eligible or liquid | Quarterly reserve coverage and liquidity evidence | Pause the pilot if the hard reserve rule fails |
| Signal uses unavailable or revised information | Publication/availability dates and revision funnel | Reject or redesign if point-in-time evidence fails |
| Holdout underperforms after costs | Gross and net holdout versus the naive benchmark | Stop if the frozen failure rule triggers |
| Allocation moves materially under changed inputs | Objective, lag, cost, and constraint stress | Reopen the mandate if the action range reverses |
| Turnover or concentration exceeds the mandate | Annual turnover and issuer-level weights | Reject implementation until the breach is resolved |

## Committee action requested

The selected allocation passes the displayed mandate controls, but reject adoption and return the process for redesign now. Reverse that decision only after the final
mandate, integrated app, observed reserve evidence, point-in-time signal, cost and turnover
checks, partner cold run, changed-input evidence, and derivative-risk disclosure are complete.

## Open items before freezing

- Complete the partner cold run and record the student-owned code explanation.
- Record the three videos, correct their transcripts, and add the final evidence timestamps.
- Reconcile this memo to the final visible output, validation record, and frozen repository commit.

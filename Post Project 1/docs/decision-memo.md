AI announcement: I used OpenAI Codex to help organize the Project 2 application, calculations, and documentation. I independently review the evidence, checks, and recommendation; the analysis and decision remain mine.

Education, not investment advice: This is a FIN 43900 course project and learning demonstration, not investment advice.

# Week 12 Prototype Decision Memo - Historical Draft

This document preserves the earlier Lab 15 studio position. The current Project 2 decision is in
[Project 2/docs/decision-memo.md](../../Project%202/docs/decision-memo.md).

## Decision and committee ask

**Provisional recommendation: pilot, not adopt.** Authorize only a bounded analysis or small pilot
after the actual reserve definition, mandate controls, costs, and point-in-time signal checks pass.
Do not treat the current classroom controls or TLT reserve proxy as a final investment mandate.

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
October 2021 through September 2026. The current runnable prototype reports:

| Estimate window | Estimated return | Estimated volatility | Reserve proxy |
|---|---:|---:|---:|
| Full history | 6.89% | 13.94% | 20% TLT |
| Last 36 months | 14.23% | 11.07% | 30% TLT |

These are historical model estimates, not forecasts. TLT is a long-duration Treasury fund and is
not automatically equivalent to cash or a twelve-month reserve.

The classroom signal test is also informative but is not yet the final integrated Project 2
strategy. Its development net return was 6.13% versus 5.33% for buy-and-hold; its untouched
holdout net return was -6.09% versus -2.09% for buy-and-hold. That result triggers the frozen
failure rule and supports caution rather than adoption.

## Mandate, assumptions, and sensitivity

The current prototype still uses classroom controls: a 6.5% objective return, a 3% reserve
minimum, long-only five-point allocation steps, and TLT marked reserve eligible. These controls
must be replaced or explicitly approved as the student's final mandate before submission.

The most consequential sensitivity is the reserve classification. Turning off TLT's reserve flag
with the current 3% minimum produced no feasible portfolio. That result makes the reserve evidence
the first reversal claim to resolve.

## Risks, failure conditions, and monitoring

| Risk or failure condition | Monitor | Reversal trigger |
|---|---|---|
| Reserve asset is not eligible or liquid | Quarterly reserve coverage and liquidity evidence | Pause the pilot if the hard reserve rule fails |
| Signal uses unavailable or revised information | Publication/availability dates and revision funnel | Reject or redesign if point-in-time evidence fails |
| Holdout underperforms after costs | Gross and net holdout versus the naive benchmark | Stop if the frozen failure rule triggers |
| Allocation moves materially under changed inputs | Objective, lag, cost, and constraint stress | Reopen the mandate if the action range reverses |
| Turnover or concentration exceeds the mandate | Annual turnover and issuer-level weights | Reject implementation until the breach is resolved |

## Committee action requested

Approve a conditional pilot only after the final mandate, integrated app, holdout panel, validation
record, partner cold run, and changed-input evidence are complete. Otherwise, reject adoption and
return the process for redesign.

## Open items before freezing

- Select and document the final mandate and numerical constraints.
- Integrate the point-in-time signal, frozen rule, holdout, placebo, costs, and selection ledger.
- Add visible baseline and mandate verdicts to the app.
- Complete the Locked Changed-Input Record with a human-authored prediction before execution.
- Reconcile this memo to the final visible output and validation record.

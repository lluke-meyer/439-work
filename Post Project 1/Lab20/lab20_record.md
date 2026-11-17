# Lab 20 - Project 2 Changed-Input Record

November 15, 2026.

## Changed input

- Input changed: Objective return
- Units: Annual percentage
- Old value: 9.00%
- New value: 10.50%
- Prediction timestamp: 11/15/2026 @ 6:45 PM
- Pre-run commit: `44ee60ecada51f6751c5d4490a68463f6ebb2431` base HEAD; Project 2 changes were uncommitted in the working tree.
- Expected output direction: Down
- Expected decision effect: Fewer portfolios will achieve `PASS` status.

## Actual result

- Actual output direction: Down
- Actual decision effect: The default six-fund result still passed the return gate at 10.68%,
  but all ten theme portfolios returned `NO FEASIBLE MIX`. The full process gate remained
  `REJECT / REDESIGN`.
- Matched or diverged: Matched.
- Failure diagnosis: The higher return target made the allocation screen stricter under the
  reserve, ticker-weight, overlap, exposure-policy, and allocation-step constraints. Drawdown,
  turnover, and frozen holdout failures remained unchanged.

## Lab 20 status

- [x] Changed-input prediction and result recorded.
- [ ] Run the partner cold check from the README, if required by Brightspace.
- [ ] Explain the portfolio and backtest code without AI assistance.
- [x] First issue reviewed: no code fix was needed; the 400% development turnover is a real result of four full-position switches and remains disclosed.
- [x] State the final decision and reversal condition.

Final decision: `REJECT / REDESIGN` - do not adopt or fund a live pilot while drawdown, turnover,
holdout, reserve, liquidity, issuer, point-in-time, or derivative-governance evidence remains open.
Reversal condition: reconsider adoption only after those checks pass and the partner cold run,
recording package, and final frozen commit are complete.

The detailed Project 2 validation record points here from `Project 2/docs/validation-and-ai-use.md`.

###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

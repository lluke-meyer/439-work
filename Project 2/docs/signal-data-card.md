AI announcement: I used OpenAI Codex to help organize this data card and selection ledger. I independently reviewed the timing rule, test boundary, and decision; the analysis remains mine.

Education, not investment advice: This is a FIN 43900 course project and learning demonstration, not investment advice.

# Signal data card and selection ledger

## Frozen signal

| Item | Frozen value |
|---|---|
| Decision question | Does a month-end card-spend signal improve the next-month equity-versus-bills decision after costs? |
| Signal | Monthly card-spend change from the Lab 18 classroom table |
| Event time | Month-end measurement for month `t` |
| Availability time | Available after the month-end publication point; the position for month `t+1` uses the signal from month `t` |
| Point-in-time rule | One-month lag; no current-month signal is used to choose the current-month position |
| Rule | Signal above 0% selects the equity fund; signal at or below 0% selects Treasury bills |
| Universe | One equity fund and Treasury bills in the classroom rule |
| Development | January-December 2025 |
| Holdout | January-June 2026, run once and left untouched |
| Benchmark | Buy-and-hold equity fund |
| Trading cost | 0.10% whenever the position switches |
| Failure rule | Stop if holdout net return trails buy-and-hold |

The source table and original frozen rule card are archived in `Post Project 1/Lab18/holdout/`. The
Project 2 implementation mirrors that rule in `backtest.py`; the holdout is not retuned by the
sidebar sensitivity controls.

## Selection ledger

| Candidate or diagnostic | Lag | Threshold | Universe | Result | Decision |
|---|---:|---:|---|---|---|
| Card-spend change rule | 1 month | `> 0%` for equity; otherwise bills | Equity fund / Treasury bills | Development net 6.13%; holdout net -6.09% versus -2.09% buy-and-hold | Frozen rule; reject after holdout failure |
| Current-month timing diagnostic | 0 months | Same `> 0%` threshold | Equity fund / Treasury bills | Development net rises to 17.72%, showing look-ahead sensitivity | Rejected as leakage; not used for the holdout |

No other signal, threshold, universe, or lag was selected for Project 2. That limitation is disclosed
instead of presenting an undisclosed search as evidence of rigor. A different rule would be a new
hypothesis and would need a new prospective holdout.

## Data boundaries and limitations

- The classroom signal table runs from December 2024 through June 2026.
- The December 2024 signal is needed to choose the January 2025 position.
- The rule uses a one-month lag because a current-month signal cannot be assumed available before the current-month return is realized.
- The classroom table is a course-authored input, not a live card-spend data feed. The app does not claim a public production-data source for it.
- The holdout failure is a decision result, not a reason to change the rule after seeing the holdout.

## Current decision

The frozen rule is useful as a transparent validation example but is not adoptable as presented.
Its development result did not survive the untouched holdout after costs, so the current committee
decision remains `REJECT / REDESIGN`.

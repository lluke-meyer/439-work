AI announcement: I used OpenAI Codex to help organize this data card and selection ledger. I am responsible for the timing rule, checks, and decision.

Education, not investment advice: This is a FIN 43900 course project and learning demonstration, not investment advice.

# My Signal Data Card and Selection Ledger

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

I keep the source table and original frozen rule card in `Post Project 1/Lab18/holdout/`.
I carried that rule into `backtest.py`. The sidebar sensitivity controls do not retune
the frozen holdout.

## Selection ledger

| Candidate or diagnostic | Lag | Threshold | Universe | Result | Decision |
|---|---:|---:|---|---|---|
| Card-spend change rule | 1 month | `> 0%` for equity; otherwise bills | Equity fund / Treasury bills | Development net 6.13%; holdout net -6.09% versus -2.09% buy-and-hold | Frozen rule; reject after holdout failure |
| Current-month timing diagnostic | 0 months | Same `> 0%` threshold | Equity fund / Treasury bills | Development net rises to 17.72%, showing look-ahead sensitivity | Rejected as leakage; not used for the holdout |

I selected no other signal, threshold, universe, or lag for Project 2. I disclose that
narrow search instead of implying I tested more than I did. A different rule would be a
new hypothesis requiring a new, prospective holdout.

## Data boundaries and limitations

- I use the classroom table from December 2024 through June 2026. The December 2024
  signal sets the January 2025 position.
- I lag the signal one month because I cannot assume a current-month reading was
  available before that month's return.
- I use a course-authored table, not a live card-spend feed or a production data source.
- I keep the holdout failure as evidence; I do not change the tested rule after seeing it.

## Current decision

I can explain and reproduce this rule, but I would not adopt it. Its development gain
did not survive the untouched, after-cost holdout. My committee call remains
`REJECT / REDESIGN`.

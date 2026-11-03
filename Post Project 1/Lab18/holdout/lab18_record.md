# Lab 18 — Holdout Test

## D — Define

Does a rule that worked in development still work on months it has never seen — after costs?

The frozen rule uses the month-end card-spend signal to choose the next month's position. A
positive signal selects the equity fund; a non-positive signal selects Treasury bills. The test
starts in bills, applies a one-month lag, charges 0.10% whenever the position switches, and
compares the rule with buy-and-hold.

## R — Represent

The rule was frozen in the [Lab 18 rule card](lab18_rule_card.md) before the backtest was built.
The training table contains the December 2024 signal needed to select the January 2025 position,
then monthly signals and equity-fund returns through June 2026.

| Input | Frozen value |
|---|---|
| Lag | 1 month |
| Switch cost | 0.10% |
| Bills return | 0.30% per month |
| Development | January–December 2025 |
| Holdout | January–June 2026, used once |
| Benchmark | Buy-and-hold equity fund |
| Failure rule | Stop if holdout net trails buy-and-hold |

## I — Implement

Run the backtest from the FIN 439 folder:

```bash
"Project 1/.venv/bin/python" "Post Project 1/Lab18/backtest.py"
```

The complete implementation is [`backtest.py`](backtest.py). Editable inputs are at
[lines 6–33](backtest.py#L6-L33). The one-month lag selects each month's position from the prior
month's signal at [lines 58–69](backtest.py#L58-L69). Switch costs and compounded gross/net
returns are calculated at [lines 71–103](backtest.py#L71-L103). The holdout starts from the
development ending position at [lines 122–126](backtest.py#L122-L126), and the failure rule is
evaluated at [lines 135–139](backtest.py#L135-L139).

## V — Validate

The normal run matched the Lab 18 known answer:

| Period | Rule gross | Rule net | Buy-and-hold | Switches |
|---|---:|---:|---:|---:|
| Development | 6.55% | 6.13% | 5.33% | 4 |
| Holdout | −5.52% | −6.09% | −2.09% | 6 |

The failure rule is **triggered** because the holdout net return trails buy-and-hold by 4.00
percentage points. Each switch moves the full position, so the development run has 400% one-way
turnover and the holdout has 600% one-way turnover.

The leakage test also passed. Running the same code with `LAG_MONTHS = 0` in memory produced a
development net return of 17.72%. That jump shows why the one-month lag is required: the rule would
otherwise trade on the current month's signal before that signal could have been available.

## E — Evolve

The frozen rule should not be tuned against the June 2026 holdout. Any revised rule is a new
hypothesis and needs new, untouched months for evaluation. The next planned extension is the Lab
19 placebo and the student's own admitted Lab 17 series.

## R — Reflect

The rule looked successful in development, where its 6.13% net return exceeded the 5.33%
buy-and-hold benchmark. The untouched holdout gave the opposite decision: the rule lost 6.09% net
while buy-and-hold lost only 2.09%. The holdout therefore fails the stated rule and the decision is
**stop**.

The pre-build rule-card commit time is intended to show that the signal, lag, cost, periods,
benchmark, and failure rule were specified before the backtest results were available. Commit and
publication remain pending final student review.



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

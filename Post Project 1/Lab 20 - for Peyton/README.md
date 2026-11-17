# Lab 20 - Peyton cold-run handoff

This folder is for Peyton's independent Project 2 cold run and code question. The runnable product is the canonical `Project 2/` folder in this repository. Use that copy so the check tests the same app and README a committee reviewer would use.

## First pass - README only

Luke gives Peyton only the repository link. Peyton opens the [Project 2 README](../../Project%202/README.md) in his own folder and follows its setup and run instructions without coaching. He records the commands he actually used, the first failure (or `None`), elapsed time, and where he found the decision in [peyton-cold-run.md](peyton-cold-run.md). He changes one bounded control and checks whether he can read the allocation mandate and full-process verdict.

After the first pass, Luke fixes the first failure and pushes the fix, or records that no fix was needed. Peyton reruns and records the outcome. Do not fill in his observations for him.

## Canonical Project 2 files

| Purpose | File |
|---|---|
| Start here and run the app | [README.md](../../Project%202/README.md) |
| Python dependencies | [requirements.txt](../../Project%202/requirements.txt) |
| Web app and committee verdict | [app.py](../../Project%202/app.py) |
| Portfolio calculation | [portfolio.py](../../Project%202/portfolio.py) |
| Frozen signal and holdout | [backtest.py](../../Project%202/backtest.py) |
| Price retrieval and fallback | [market_data.py](../../Project%202/market_data.py) |
| Reproducible default prices | [prices.csv](../../Project%202/prices.csv) |
| Result readable without running code | [visible-output.txt](../../Project%202/outputs/visible-output.txt) |
| Committee decision and reversal condition | [decision-memo.md](../../Project%202/docs/decision-memo.md) |
| Validation and changed-input record | [validation-and-ai-use.md](../../Project%202/docs/validation-and-ai-use.md) |
| Point-in-time signal boundary | [signal-data-card.md](../../Project%202/docs/signal-data-card.md) |

## Code explanation

After the cold run, Luke opens the code that produces a decision number and explains it line by line without AI. Peyton asks one question. Record the code location, question, and any unresolved gap in the cold-run note. The conversation itself is not a Project 2 deliverable; carry over a discovered bug, limitation, or corrected claim to the Project 2 validation record.

The changed-input exercise is already recorded separately in [Lab 20](../Lab20/lab20_record.md). This handoff does not repeat it.

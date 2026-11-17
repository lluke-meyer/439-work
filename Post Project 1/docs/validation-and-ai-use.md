AI announcement: I used OpenAI Codex to help organize the Project 2 application, calculations, and documentation. I independently review the evidence, checks, and recommendation; the analysis and decision remain mine.

Education, not investment advice: This is a FIN 43900 course project and learning demonstration, not investment advice.

# Week 12 Prototype Validation and AI Use - Historical Draft

This document preserves the earlier Lab 15 studio evidence. The current Project 2 validation
record is [Project 2/docs/validation-and-ai-use.md](../../Project%202/docs/validation-and-ai-use.md).

## Run identity

- Working repository: `439-work`
- Working path: `Post Project 1/`
- Current prototype command: `.venv/bin/python -m streamlit run "Post Project 1/Lab15/app.py"`
- Current evidence boundary: bundled monthly adjusted-close prices through September 1, 2026;
  classroom signal data through June 2026.
- Final frozen commit: pending Project 2 integration and Lab 20 changed-input run.

## Validation status

| Required check | Current evidence | Status |
|---|---|---|
| Known-answer/manual baselines | Lab 14 baseline and Lab 15 engine checks | Complete for classroom inputs; integrate into final app |
| Constraint and unit checks | Portfolio engine validates weights, covariance dimensions, correlations, and bounds | Complete for current engine; final mandate pending |
| Point-in-time and revision audit | Labs 16-17 provenance funnel and M2SL vintage exercise | Complete as lab evidence; connect final signal |
| Naive benchmark and true holdout | Lab 18 classroom rule versus buy-and-hold, now visible in the Lab 15 app | Complete for classroom rule; final Project 2 signal pending |
| Costs and stress run | Switch cost in Lab 18; bounded lag/cost controls and TLT reserve-flag stress in the app | Partial; student review and final constraints pending |
| Placebo/falsification test | Not yet integrated into the Project 2 app | Pending |
| Cold run and visible output | Local app run reached the bundled six-fund result with six dataframes, seven metrics, zero exceptions, and zero displayed errors | Local check complete; partner cold run pending |
| Highest-risk counterexample | Removing TLT reserve eligibility produced no feasible mix | AI-proposed test locally run; student disposition pending |
| Locked Changed-Input Record | No final Project 2 record yet | Pending |
| Independent AI-output check | The reserve-eligibility test was run and its limitation identified | Partial; final record needs named tool, date, and student disposition |

## Data and transformation record

- Price input: `Lab15/prices.csv`, monthly adjusted close, common window October 2021 through
  September 2026.
- Return transformation: monthly price changes, annualized expected return as monthly mean times
  12, annualized volatility as monthly sample standard deviation times square root of 12.
- Portfolio search: long-only weights on a five-percentage-point grid; feasible portfolios must
  meet the objective return and reserve minimum.
- Signal timing: the frozen classroom rule uses a one-month lag so the signal must be available
  before the position is selected.
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

The local portfolio prototype also produced 6.89% estimated return, 13.94% estimated volatility,
and a 20% TLT reserve proxy on the full bundled history. These numbers are provisional classroom
outputs and must be reconciled after the final app integration.

## Locked Changed-Input Record - pending

Before the final run, complete this record without AI assistance on the prediction:

- Input changed:
- Units:
- Old value:
- New value:
- Prediction timestamp:
- Pre-run commit:
- Expected output direction:
- Expected decision effect:
- Actual output direction:
- Actual decision effect:
- Matched or diverged:
- Failure diagnosis or reason for no change:

The original frozen rule and holdout remain locked evidence. A changed lag, cost, or estimate is a
sensitivity scenario, not permission to retune the holdout.

## Named AI-use register - working draft

| Tool/model | Interaction date | Material use | Independent disposition |
|---|---|---|---|
| OpenAI Codex - exact model/version to confirm | November 15, 2026 | Organized the Project 2 documentation, reviewed course instructions, and proposed the reserve-eligibility stress test | The test was run locally; the final student judgment and evidence record remain pending |

Before submission, add every material AI interaction, the exposed tool/model/version, the date,
the output considered, and whether it was accepted, qualified, corrected, or rejected.

## Reproducibility and access checklist

- [x] README contains a one-command local run for the current prototype.
- [x] Visible output is available through the Streamlit app and Lab 15 record.
- [ ] Final app shows baselines, mandate verdicts, frozen holdout gross/net, and bounded controls.
- [ ] Partner can run the repository from the README alone.
- [ ] Final visible output, memo, and videos use the same numbers and dates.
- [ ] No passwords, API keys, tokens, credentials, or private data are committed.

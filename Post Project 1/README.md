# Post Project 1 Labs

AI use: Codex assisted with code, lab records, and this studio setup. The Project 2 analysis and
committee decision are Luke Meyer's to verify and own; the Tuesday record contains an AI-assisted
draft for his review.

This is an educational exercise, not investment advice.

## Historical Lab 15 studio prototype

This folder holds the Labs 13–20 work inside the single
[439-work repository](https://github.com/lluke-meyer/439-work). The commands below reproduce the
Lab 15 six-fund prototype used in the Week 12 studio. The current application and submission
documents are in the separate [Project 2 folder](../Project%202/README.md).

From a fresh clone, in the repository root, set up Python once (macOS/Linux):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r "Post Project 1/requirements.txt"
```

Then run this one command:

```bash
.venv/bin/python -m streamlit run "Post Project 1/Lab15/app.py"
```

The browser opens the **Bundled six-fund universe** using
[`Lab15/prices.csv`](Lab15/prices.csv) by default. The first **Current estimates** result and the
five-level table are the visible output. No upload or SEC/FRED key is needed for this run.
The sidebar can switch to Meridian classroom inputs, choose the last 36 monthly returns, or
upload another price CSV. The bundled prices end September 1, 2026; their source and limitations
are in the [Lab 15 record](Lab15/lab15_record.md#price-data-and-sources).

Evidence map: [mandate](Lab13/mandate.json) · [classroom baselines](Lab14/lab14_record.md) ·
[portfolio app and stress controls](Lab15/lab15_record.md) ·
[point-in-time rule](Lab16/lab16_record.md) · [vintage data exercise](Lab17/lab17_record.md) ·
[investor research screens](Lab18/lab18_record.md) and [panel](Lab19/lab19_record.md) ·
[Tuesday studio record](Lab19.1/tuesday_studio_record.md) ·
[Thursday Q&A catch-up](Lab19.2/lab19.2_record.md) ·
[Lab 20 changed-input record](Lab20/lab20_record.md) ·
[Week 12 memo draft](docs/decision-memo.md) ·
[Week 12 validation draft](docs/validation-and-ai-use.md).

This is a dated prototype record. The integrated app, current mandate, validation, decision memo,
and November 17 partner check are in [Project 2](../Project%202/README.md). See the
[Project 2 brief](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/projects/project-2-investment-management-application.md)
for the final requirements.

## Lab folder convention

All FIN 439 labs after Project 1 belong in this folder using one subfolder per lab:

```text
Post Project 1/
  Lab13/
  Lab14/
  Lab15/
  ...
```

## Submission record required

Every lab must include one submission-ready record named `lab##_record.md`, following
[`Lab15/lab15_record.md`](Lab15/lab15_record.md) as the current model. The record is the lab's
single written handoff for GitHub and Brightspace and should include, as applicable:

- The decision question or assignment objective.
- Exact commands needed to run the work.
- Inputs, assumptions, data sources, and constraints.
- Required calculations, checkpoints, results, and interpretation.
- The student's final call plus any remaining human-review items.
- The required three-line disclosure block at the bottom of the document.
- Links to the lab's code-heavy files and important implementation blocks.
- For completed in-class work, record the item as exactly `Completed during class.`

Update the record whenever its code, data, controls, or reported results change so it remains
submission-ready. Use relative links with line anchors where practical, and update them when code
lines move. Confirm each assignment's specific link or upload requirements in Brightspace.

## Disclosure convention

Do not add a separate custom Chat/Codex explanation to a lab document. Every submitted lab document,
including code and the written record, should end with this exact three-line block. In Python files,
the lines are valid comments; in Markdown files, they render as headings.

```text
###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.
```

Each lab folder should otherwise contain only the required code and source data. Keep validation
inside the runnable code when practical. Do not create separate README, trace, saved-output,
disclosure, or optional-challenge files unless the course specifically requires them. Do not place
new lab work in `Pre Project 1` or `Project 1`.

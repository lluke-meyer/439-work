# Post Project 1 Labs

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

# Lab 16 — Provenance Gate

## Decision question

On the day a decision would have been made, what did the data actually say, and how much of the
signal became visible only later?

## Run command

From the FIN 439 folder:

```bash
"Project 1/.venv/bin/python" "Post Project 1/Lab16/asof.py"
```

The file uses only the Python standard library. The editable inputs are at the top of `asof.py`:
the fictional card-spend table and the decision date, initially `2026-03-31`.

## Rules implemented

The filter applies the assignment's rules in order and keeps each original row number:

1. Quarantine a row with no ticker.
2. Remove an exact duplicate.
3. Remove rows published after the decision date.
4. For a ticker and measured month with multiple knowable publications, keep the latest publication
   as the revision.

The as-of signal is the percent change from the previous measured month to the latest measured
month remaining in the panel. The naive signal uses each ticker's latest publication without an
as-of cutoff.

## Known-answer validation

The run on the supplied training table produced the required row funnel:

| Funnel step | Removed rows |
|---|---|
| Quarantined: no ticker | 11 |
| Exact duplicate | 7 |
| Published after 31 March 2026 | 3, 8, 10 |
| Older vintage replaced by a revision | 2 |
| As-of panel | 1, 4, 5, 6, 9, 12 |

The computed signals were:

| Ticker | As-of signal | Naive signal |
|---|---:|---:|
| AAA | +1.98% (2026-02) | +5.83% (2026-03) |
| BBB | −1.02% (2026-02) | −5.15% (2026-03) |
| CCC | +0.91% (2026-02) | +1.82% (2026-02) |

The later-date check also passes: changing the decision date to `2026-04-15` makes the as-of
panel use the latest available vintage for every ticker, so the as-of signals equal the naive
signals ticker for ticker.

## Interpretation and reflection

The revision rule removed row 2, which matters because the March 25 revision changes AAA's
knowable February index from 104.0 to 103.0. The naive AAA signal of +5.83% uses the March value
published April 10, so it was not knowable on March 31. A backtest using that naive column would
claim a stronger and more timely signal than a trader could actually have observed: look-ahead
bias.

The measured month and publication date answer different questions. A February observation can be
useful on March 10, while a March observation published April 10 cannot be used in a March 31
decision. Revisions are also point-in-time information: the revised value is usable only after its
publication date.

## Checkout items

- Submit the GitHub links to `asof.py` and this record individually.
- Complete the Lab 16 Brightspace quiz if required by the course module.
- Explain the revision-selection block to the partner and answer the partner's code question.
- Keep the script unchanged for Thursday's Lab 17 ALFRED series exercise unless the instructor
  directs otherwise.

## Chat/Codex disclosure

Chat/Codex translated the Lab 16 instruction into a standard-library filter, preserved source row
numbers, printed the funnel and signal comparison, and documented the known-answer and later-date
checks. The student should read and explain the revision-selection logic before submission and
complete the individual Brightspace checkout.

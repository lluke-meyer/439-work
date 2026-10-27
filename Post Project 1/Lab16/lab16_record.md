# Lab 16 — Provenance Gate

This lab asked a simple question: if I had made a decision on March 31, 2026, what data would I actually have had? The main lesson was that the month a number measures is not the same as the date the number became available. If I ignore that distinction, a backtest can use information that did not exist yet.

## D — Define

The decision date for the training table is March 31, 2026. A row is usable only when its publication date is on or before that date. The goal is to build a point-in-time panel for three fictional retailers and compare its signals with a naive panel that uses the latest publication, even when that publication came later.

## R — Represent

The input table is stored directly in `asof.py`. Each row contains its original row number, ticker, measured month, publication date, and index value. Keeping the original row number makes every removal traceable.

The filter uses four rules in this order:

1. Quarantine a row with no ticker.
2. Remove an exact duplicate.
3. Remove any row published after the decision date.
4. When a ticker and measured month have multiple knowable publications, keep the latest one as the revision.

The as-of signal is the percent change from the previous measured month to the latest measured month remaining in the point-in-time panel. The naive signal uses each ticker's latest publication without applying the decision-date cutoff.

## I — Implement

Run the script from the FIN 439 folder with:

```bash
"Project 1/.venv/bin/python" "Post Project 1/Lab16/asof.py"
```

The script uses only the Python standard library. The decision date and training rows are editable at the top. The calculation converts publication strings to dates, applies the four rules, prints the row funnel, shows the remaining panel, and calculates both signal columns from the input data rather than typing the answers into the output.

## V — Validate

The March 31 run produced the required funnel:

| Funnel step | Removed rows |
|---|---|
| Quarantined: no ticker | 11 |
| Exact duplicate | 7 |
| Published after March 31 | 3, 8, 10 |
| Older vintage replaced by a revision | 2 |
| As-of panel | 1, 4, 5, 6, 9, 12 |

The computed signals were:

| Ticker | As-of signal | Naive signal |
|---|---:|---:|
| AAA | +1.98% (2026-02) | +5.83% (2026-03) |
| BBB | −1.02% (2026-02) | −5.15% (2026-03) |
| CCC | +0.91% (2026-02) | +1.82% (2026-02) |

The later-date test also passed. When I changed the decision date to April 15, 2026, the as-of signals matched the naive signals for all three tickers because every training-table publication was then available.

## E — Evolve

The next step is to use the same filter with a real monthly ALFRED series connected to the Project 2 universe. That series needs a source name, measured month, publication or release date, value, units, revision information, and download date. If a publication date cannot be established, the series should be quarantined rather than used in a backtest.

## R — Reflect

The most important removal was row 2. Row 2 reported AAA's February index as 104.0, but row 4 revised that value to 103.0 on March 25. Because the revision was available before March 31, row 4 is the value that belongs in the as-of panel.

The naive AAA signal of +5.83% uses the March value of 109.0, which was not published until April 10. The knowable signal was only +1.98%. A backtest using the naive column would therefore make the strategy look stronger and more timely than it could have been in real time. That is look-ahead bias.

The code also makes the timing distinction clear: the measured month tells me what the observation describes, while the publication date tells me when I could use it. A revision changes the value only from its publication date forward.

## Submission and disclosure

Submit the GitHub links to `asof.py` and this record individually, and complete the required Brightspace checkout. The script is ready to carry into Lab 17, where the same point-in-time logic will be applied to a real ALFRED series.

Chat/Codex helped translate the assignment instructions into the standard-library filter, preserve the original row numbers, calculate the two signal panels, and draft this record. The student remains responsible for understanding the revision-selection logic and completing the course submission requirements.

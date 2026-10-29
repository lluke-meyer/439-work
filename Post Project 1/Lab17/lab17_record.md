# Lab 17 — Point-in-Time Audit

## D — Define

Completed during class.

## R — Represent

The source table is [`m2sl_vintages.csv`](m2sl_vintages.csv). It covers the 26-month span from August 2024 through September 2026 and contains 351 nonblank vintage rows from the H.6 release snapshots, including repeated values and later ALFRED revisions.

### Data card

| Field | Evidence |
|---|---|
| Source and link | [FRED M2SL series](https://fred.stlouisfed.org/series/M2SL), [ALFRED M2SL series](https://alfred.stlouisfed.org/series?seid=M2SL), and [ALFRED vintage CSV endpoint](https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=M2SL) |
| What it measures | M2 money stock, seasonally adjusted, sourced from the Federal Reserve Board's H.6 Money Stock Measures release |
| Units | Billions of dollars, seasonally adjusted |
| Publication timing | H.6 is generally released on the fourth Tuesday of each month at 1:00 p.m.; the first retained vintage for August 2024 was published September 24, 2024, about 24 days after month-end |
| Revisions | Yes. The table preserves later ALFRED value changes, including broad revision waves in February 2025, October 2025, February 2026, and October 2026. |
| Download date | October 29, 2026 |
| Release-date cross-check | [Federal Reserve H.6 release page and release dates](https://www.federalreserve.gov/releases/h6/) |

I checked three rows directly against ALFRED: August 2024 = 21,174.9 on September 24, 2024; October 2025 = 22,298.1 on November 25, 2025; and September 2026 = 23,413.9 on October 27, 2026. The measured month and publication date are separate fields: the first says what period the aggregate describes, while the second says when the value could enter a backtest.

### Fresh-eyes attack

Completed during class.

## E — Implement

Run the complete Lab 17 audit from the FIN 439 folder:

```bash
"Project 1/.venv/bin/python" "Post Project 1/Lab17/asof.py"
```

The script preserves the Lab 16 training output, adds the three required training decision dates, reads the own-series CSV using the four course columns, applies the same provenance gate at the last 24 month-ends, and counts naive rows that were not yet published. It keeps source row numbers attached to the funnel.

The screenshot-required app is [`asof_app.py`](asof_app.py). It downloads one current FRED CSV and one ALFRED vintage CSV per selected series, caches both downloads, defaults to the four interest-rate series as the primary comparison set, keeps M2SL as a secondary series, and presents one focus chart with an optional indexed overlay of the other selected series. The chart compares current FRED data with the ALFRED version known on the selected date, followed by a table with later values and revised dates.

Run the audit script with:

```bash
"Project 1/.venv/bin/python" "Post Project 1/Lab17/asof.py"
```

Run the Streamlit app with:

```bash
"Project 1/.venv/bin/streamlit" run "Post Project 1/Lab17/asof_app.py"
```

### Code references

- [Editable decision dates, source path, and training table](asof.py#L16-L33)
- [Four-rule provenance gate](asof.py#L58-L84)
- [CSV loader and own-series vintages](asof.py#L176-L195)
- [Naive leakage rows and 24-month report](asof.py#L216-L268)
- [FRED/ALFRED downloads and caching](asof_app.py#L12-L71)
- [Series controls, focus chart, overlay, and comparison table](asof_app.py#L174-L331)

## V — Validate

The training table reproduced the known answer:

| Decision date | As-of signal | Naive rows not yet published |
|---|---|---|
| February 28, 2026 | not enough knowable months | 4, 6, 10 |
| March 31, 2026 | AAA +1.98%, BBB −1.02%, CCC +0.91% | 3, 8, 10 |
| April 30, 2026 | equal to the naive signal | none |

The own-series run covers the last 24 complete month-ends, October 31, 2024 through September 30, 2026. The final report prints each date's as-of signal, funnel counts, as-of panel size, and number of naive future rows. The M2SL table contains more revisions than the training table, which is the intended stress test of the provenance gate.

The live Streamlit AppTest completed with zero exceptions and zero displayed errors in both chart modes: one focus chart in original units and one indexed overlay chart, each with one comparison table, rendered successfully using the public FRED and ALFRED CSV downloads.

### Relevant source links

- [M2SL on FRED](https://fred.stlouisfed.org/series/M2SL)
- [DGS10 on FRED](https://fred.stlouisfed.org/series/DGS10)
- [FEDFUNDS on FRED](https://fred.stlouisfed.org/series/FEDFUNDS)
- [BAA on FRED](https://fred.stlouisfed.org/series/BAA)
- [MORTGAGE30US on FRED](https://fred.stlouisfed.org/series/MORTGAGE30US)
- [Federal Reserve H.6 release dates](https://www.federalreserve.gov/releases/h6/)

## Submission

After commit, add the GitHub links to [`asof.py`](asof.py), [`asof_app.py`](asof_app.py), [`m2sl_vintages.csv`](m2sl_vintages.csv), and this record, then complete the required Brightspace checkout.

###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

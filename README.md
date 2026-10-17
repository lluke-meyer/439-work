# CDNS Valuation Workbench - FIN 43900 Project 1

## Decision and intended user

This project supports a buy-side investment committee that currently holds no position in Cadence Design Systems (NASDAQ: CDNS). The decision is whether to initiate a position, watch/defer, or not initiate as of September 1, 2026. The current base judgment is **watch/defer - no position at the current market price**, subject to the conditions and reversal triggers documented in the final decision memo.

## What the product does

The Streamlit workbench connects a five-year three-statement pro-forma to FCFF and a DCF. It provides:

- bounded base, downside, and upside scenarios;
- a driver panel for revenue growth, gross margin, operating expenses, WACC, and terminal growth;
- five-year financial statements and FCFF;
- an enterprise-to-equity/per-share bridge;
- WACC-terminal growth sensitivity and reverse DCF;
- visible balance-sheet, cash-flow, cash-floor, and terminal-growth checks;
- a deliberate fail-loud demonstration for an incoherent terminal-growth input; and
- the current comparable-company evidence and clearly labeled open evidence gaps.

## Setup and run

Python 3.11 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

The terminal will print a local URL, normally `http://localhost:8501`.

## Reproduce the visible output without the interface

```bash
python3 project1_model.py
python3 project1_model.py --snapshot outputs/visible-output.txt
python3 -m unittest discover -s tests -v
```

## Repository map

- `app.py` - Streamlit user interface.
- `project1_model.py` - dependency-free pro-forma, FCFF DCF, scenarios, sensitivity, reverse DCF, and checks.
- `tests/test_model.py` - articulation, monotonicity, scenario-ordering, and boundary tests.
- `outputs/visible-output.txt` - frozen, human-readable executed output.
- `docs/validation-and-ai-use.md` - working validation record and the blank Locked Changed-Input Record.
- `Lab04 Project 1 Edition A.md` - preserved Edition A working file; the Brightspace receipt remains the baseline of record.
- `Lab05` through `Lab12` files - weekly development evidence retained for traceability.

## Data sources and boundaries

Material historical inputs currently come from the CDNS FY2025 Form 10-K and the source notes preserved in the weekly files. The project uses a September 1, 2026 valuation date and a $313.04 market close. The final validation record must freeze every load-bearing source, as-of date, definition, transformation, and exclusion.

## Known limitations and open requirements

- The pro-forma simplifies other assets and other liabilities by holding them flat.
- The Hexagon acquisition and subsequent quarterly updates are not yet fully incorporated.
- The 9% WACC still needs a complete independently sourced component record.
- The comparable-company work currently has a single-peer P/E reference; a consistent enterprise-value peer multiple remains required.
- Scenario ranges are analyst assumptions and must be supported in the final assumption-challenge record.
- `docs/validation-and-ai-use.md` is not complete until Luke personally records and commits the AI-off changed-input prediction, the test is executed afterward, and the result is reconciled.

## Academic and AI-use note

This report was prepared for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research or financial advice. Material AI assistance, independent checks, and dispositions belong in `docs/validation-and-ai-use.md`; the judgments remain the student's.

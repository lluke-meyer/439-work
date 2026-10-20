# CDNS Valuation Workbench - FIN 43900 Project 1

## Decision and intended user

This project supports a buy-side investment committee that currently holds no position in Cadence Design Systems (NASDAQ: CDNS). The decision is whether to initiate a position, watch/defer, or not initiate as of September 1, 2026. The current base judgment is **watch/defer - no position at the current market price**, subject to the conditions and reversal triggers documented in the final decision memo.

## What the product does

The Streamlit workbench connects a five-year three-statement pro-forma to FCFF and a DCF. It provides:

- bounded base, downside, and upside scenarios;
- a driver panel for revenue growth, gross margin, operating expenses, WACC, and terminal growth;
- five-year financial statements and FCFF;
- an enterprise-to-equity/per-share bridge;
- WACC-terminal growth sensitivity and a market-implied expectations dashboard;
- a result-based committee engine with disclosed initiation and monitoring rules;
- correlated semiconductor-cycle regimes that move operations, beta, and WACC together;
- a separate, adjustable Hexagon D&E acquisition-economics overlay;
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

- `app.py` - interactive committee dashboard, industry regimes, and acquisition overlay.
- `project1_model.py` - dependency-free pro-forma, FCFF DCF, decision rules, market-implied tests, scenarios, acquisition overlay, and checks.
- `tests/test_model.py` - articulation, monotonicity, scenario-ordering, and boundary tests.
- `outputs/visible-output.txt` - frozen, human-readable executed output.
- `docs/research-evolution.pdf` - repository copy of the Edition A-to-B research-evolution record.
- `docs/decision-memo.pdf` - repository copy of the two-page investment-committee memo.
- `docs/validation-and-ai-use.pdf` - repository copy of the validation and named AI-use record.
- `docs/validation-and-ai-use.md` - working validation and AI-use record, including the completed Locked Changed-Input Record.
- `docs/wacc-and-ev.md` - internal source-and-calculation worksheet; not a Brightspace deliverable.
- `recording-package/` - timed screen plan and archived recording scripts for all three required videos.
- `docs/transcript-video-1.txt` through `docs/transcript-video-3.txt` - corrected transcripts, final URLs, durations, evidence timestamps, and the frozen model commit.
- `submission/` - capitalized Brightspace-ready copies where macOS cannot store both filename casings in `docs/`.

The original Lab 04-Lab 12 working files are stored separately in the sibling `../439-Work/` folder. They are development history, not part of the final runnable Project 1 package. The Brightspace receipt preserved in `docs/research-evolution.pdf` remains the Edition A baseline of record.

## Data sources and boundaries

Material historical inputs come from the CDNS FY2025 Form 10-K and the source record preserved in `docs/validation-and-ai-use.md` and `docs/wacc-and-ev.md`. The sourced 10.0% WACC uses September 1, 2026 Treasury data, Damodaran's 2025 ERP and January 2026 industry beta, and Cadence's Q2 2026 filing. The Synopsys EV/TTM-revenue cross-check uses the latest filings and shares available before September 1. The project uses a September 1, 2026 valuation date and a $313.04 market close.

## Known limitations and open requirements

- The pro-forma simplifies other assets and other liabilities by holding them flat.
- The Hexagon acquisition is modeled as a separate, sourced-fact/analyst-assumption overlay; it is not a full post-acquisition three-statement rebuild.
- The WACC uses an industry beta and a recent effective debt-cost proxy rather than a security-level historical beta and quoted debt yield.
- The P/E and EV/TTM-revenue cross-checks both rely on one qualified peer, Synopsys, whose Ansys acquisition reduces comparability.
- Scenario ranges are analyst assumptions and must be supported in the final assumption-challenge record.
- The 15% initiation threshold is a committee-policy assumption; the do-not-initiate boundary is the independently modeled $57.20 downside value.
- The integrated DCF retains FY2025 opening balances. The EV/revenue cross-check uses a separately disclosed June 2026 CDNS bridge and must not be substituted into the DCF without rebuilding the operating model.

## Academic and AI-use note

This report was prepared for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research or financial advice. Material AI assistance, independent checks, and dispositions belong in `docs/validation-and-ai-use.md`; the judgments remain the student's.

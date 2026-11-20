AI announcement: I used OpenAI Codex to help write and organize the Project 2 application, calculations, tests, and documentation. I independently review the evidence, checks, and recommendation; the analysis and decision remain mine.

Education, not investment advice: This is a FIN 43900 course project and learning demonstration, not investment advice.

# Project 2 - Portfolio Decision Workbench

## Decision and intended user

This project supports an analyst advising an investment committee. The working ten-fund universe
is VOO, VTI, VNQ, VWO, FBTC, FBND, FIVA, SGOV, TLT, and TIP. All ten are initially selected;
TLT and TIP can be removed or assigned zero weight. At the current 9% return target and 10% FBTC cap, the app finds **no
feasible allocation**. The full-process decision is **reject/redesign** because the frozen
timing test fails turnover and holdout checks and the new price panel is not total-return data.

## What the product does

The Streamlit workbench connects a constrained portfolio search with transparent allocation
baselines and a frozen signal backtest.

The committee decision has two layers: numerical allocation feasibility and evidence for adopting
the process. The new mandate finder takes a fixed, user-chosen weight mix and shows the limits
required to admit it. It does not relax the committee's working mandate or erase the separate
failed process checks. The classroom equity-versus-bills signal is not realized performance of
this ETF mix.

It provides:

- ten observed funds and a 3-10 fund-slot selector, with all ten initially selected;
- ten six-fund starting themes using only the new universe;
- a fixed-weight mandate finder for return, reserve, concentration, overlap, gross exposure,
  shorting, and historical price drawdown boundaries;
- an Auto-Pass numerical button that maximizes scenario return on the selected-fund grid,
  preserves reserve and risk limits, lowers only an unattainable return target, and can restore prior inputs;
- a one-click full-process pass check that lists failed and unresolved gates with the evidence needed to clear them;
- a plain committee-review header, a collapsible seven-step walkthrough, and a floating allocation/process verdict;
- a ten-theme allocation audit that separates allocation PASS from
  full-process adoption;
- a frozen Nasdaq monthly Close/Last price panel, optional Yahoo live pull, and CSV upload;
- bounded objective-return and reserve-minimum controls;
- a 9% estimated-return target and 1% reserve floor for the current working mandate;
- bounded net-exposure search with up to 10% short weight and 110% gross exposure by default, plus up to five feasible risk levels;
- a 40% general ticker cap, separate 10% FBTC cap, SGOV-only reserve flag, and two-part overlap screen;
- equal-weight and inverse-volatility baselines with visible mandate verdicts;
- a mandate-survival gate separating numerical screens from return-data quality, liquidity,
  issuer, derivative, turnover, and holdout evidence;
- a frozen one-month-lag classroom holdout with gross and net results;
- a linked signal data card and selection ledger, including the zero-lag leakage diagnostic;
- bounded signal-lag, switch-cost, and bills-return sensitivity controls;
- visible failure status when holdout net trails buy-and-hold.

## Setup and run

Python 3.11 or newer is recommended.

From the FIN 439 repository root, use the commands for your shell.

macOS/Linux (Bash):

```bash
cd "Project 2"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Windows (PowerShell):

```powershell
cd "Project 2"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The terminal will print a local URL, normally `http://localhost:8501`.

The sidebar's **Price source** control defaults to the bundled CSV. Select **Yahoo Finance (live)**
to pull a common monthly history for the available tickers. The adapter uses adjusted close when
the endpoint supplies it and otherwise falls back to close; verify this before mixing sources or
interpreting returns. The pull is cached for
one hour so a committee discussion does not repeatedly hit the public endpoint. If Yahoo is
unavailable or rate-limits the request, the app reports the problem and falls back to the bundled
file. The live endpoint is public and unofficial, so the source, date window, and fallback status
must be recorded before using the output as evidence.

## Reproduce the validation output

On macOS/Linux, run these commands from `Project 2/` with the virtual environment activated:

```bash
python -m unittest discover -s tests -v
python -c "from backtest import run_backtest; r=run_backtest(); print(r['development']['net'], r['holdout']['net'])"
```

On Windows PowerShell, run the same checks through the virtual-environment interpreter:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -c "from backtest import run_backtest; r=run_backtest(); print(r['development']['net'], r['holdout']['net'])"
```

The repository also includes [`outputs/visible-output.txt`](outputs/visible-output.txt), a readable
snapshot of the current executed result for a grader who does not run the app.

## Repository map

- `app.py` - interactive portfolio search, baseline verdicts, holdout panel, and bounded controls.
- `portfolio.py` - portfolio estimates, covariance, allocation search, and efficient risk levels.
- `mandate_finder.py` - exact numerical mandate boundaries for a fixed chosen mix.
- `auto_pass.py` - highest-return numerical allocation under the selected reserve and risk limits.
- `process_audit.py` - full-process blocker report that preserves gate results and proposes next evidence.
- `backtest.py` - reusable Lab 18 development/holdout calculation used by the app.
- `prices.csv` - frozen month-end Close/Last prices for the ten-fund universe.
- `data/prices-source.md` - source URLs, transformation, checksums, and return-data limitation.
- `tests/` - known-answer and Streamlit smoke checks.
- `outputs/visible-output.txt` - frozen readable snapshot of the current result.
- `docs/decision-memo.md` - investment-committee recommendation and conditions.
- `docs/validation-and-ai-use.md` - sources, tests, limitations, AI-use register, and Locked Changed-Input Record.
- `docs/evidence/peyton-cold-run-rerun.md` - Peyton's first setup failure and assisted continuation; Luke's completion confirmation is in the validation record.
- `docs/signal-data-card.md` - point-in-time timing rule, signal boundaries, and tested selection ledger.
- `recording-package/manifest.md` - final links, evidence index, and freeze checklist.
- `recording-package/` - working scripts and recording guide; replace draft placeholders after the final mandate and app output are frozen.

## Data sources and boundaries

The bundled file has 33 common monthly closes, January 2024 through September 2026, for all ten
funds. [The source record](data/prices-source.md) lists the Nasdaq historical URLs, SHA-256
checksums, transform, and exact limitation. These closes **exclude cash distributions**. Thus
the app uses their price changes for volatility, correlation, and drawdown screens, while the
annual return inputs are explicit, editable **illustrative scenario assumptions**. They are not
verified forecasts or historical total returns. The bundled panel offers full history (32
monthly returns) or the last 24 returns for price-based risk estimates. A 36-return window is
available only for longer uploaded or live panels. The window does not change the illustrative
expected-return assumptions. Uploaded or live data have their own source boundary. The classroom
signal table remains separate and uses a one-month lag.

The current working mandate proposes a five-year investment horizon, quarterly committee review,
and annual core-portfolio rebalancing. It uses a 9% scenario annual return target before trading costs, a 1%
reserve floor, a 30% drawdown review trigger for the requested moderately risky/risky posture, a 75% liquidity floor within 10 business days, a 25% annual one-way
turnover limit, a 40% maximum long ticker weight, a separate 10% FBTC cap, a 10% maximum short ticker weight, a 110% gross-exposure
ceiling, and a 60% broad-exposure overlap cap. Shorting and limited borrowing are permitted within
those bounds. Derivatives are permitted for hedging, but derivative contracts, margin, Greeks,
financing spreads, and counterparty exposure are not priced by this app and require separate review.
These are analyst-proposed Project 2 controls, separate from the Lab 13 Meridian teaching case;
the committee must approve them before implementation.
The app evaluates a candidate allocation and historical sensitivity; it does not execute the
proposed rebalancing schedule. The separately tested monthly timing component would require an
explicit policy exception and still fails its turnover and holdout gates.

Only [SGOV](https://www.ishares.com/us/products/314116/ishares-03-month-treasury-bond-etf)
counts as a working reserve candidate. [TLT](https://www.ishares.com/us/products/239454/ishares-20-plus-year-treasury-bond-etf)
is optional long-duration risk exposure, never a cash substitute. The committee still must
approve its final reserve and liquidity policy.

The overlap screen has two layers: gross broad exposure buckets such as U.S. equity beta and long
Treasuries, plus a pairwise screen for selected active funds whose estimated correlation is at least
70%. The pairwise screen caps the combined weight at 70% by default. Neither screen replaces
holdings-level look-through.

## Current results and limitations

At the default 9% target and 10% FBTC cap, no mix of the ten initially selected funds clears
all numerical allocation controls under the stated assumptions. The inverse finder shows why:
an equal-weight ten-fund mix requires a return target no higher than 6.45%, while its 10%
FBTC weight exactly meets the proposed bitcoin cap. These are compatibility
boundaries, not suggested changes to policy. Lowering the objective to 7.5% is a live
sensitivity that can yield a numerical PASS, but the full process still rejects/redesigns.
The Auto-Pass button instead finds the highest scenario return available on the 10% weight
grid under the unchanged reserve and risk controls: 7.75%, with VOO 40%, VTI 20%, FBTC
10%, FIVA 20%, and SGOV 10%. It sets the displayed return target to 7.7% and those weights,
producing a numerical PASS. This is a sensitivity proposal, not approval of a weaker
mandate or a passing full process. If no allocation satisfies the reserve and risk controls,
the button reports that instead of waiving them. The adjacent restore button returns the
previous target and chosen weights after the sensitivity. Funds may remain selected with
zero weight in the optimized mix.
The full-process pass check reports the current failed and review gates and the work needed
for a real pass. It does not change thresholds, relabel a failed holdout, or turn missing
data and committee judgment into evidence. With the frozen rule, turnover and holdout
remain failures, so no button can produce a defensible full-process PASS today.
The new price panel also remains a data-quality REVIEW because it excludes distributions.
The frozen classroom signal produces 6.13% development net and -6.09% holdout net versus -2.09%
buy-and-hold, so its failure rule triggers. The app displays that failure rather than averaging it
away.

Before submission, the remaining human-owned steps are a fresh AI-off prediction and pre-run
commit for the Locked Changed-Input Record, Luke's on-screen review of the revised ten-fund
app and mandate finder, the three revised recordings, corrected video transcripts, manifest
links and durations, access check, and frozen commit. The earlier partner cold run is the
available partner evidence; it predates the ten-fund changes and does not validate this
version. The supplied partner note also lacks a separate post-fix README-only log.
The current signal data card
and zero-lag leakage diagnostic are included in the repository; no new signal was selected after
seeing the holdout.
The mandate, final decision, derivative disclosure, and prior changed-input scenario are documented.
Luke's November 15 changed-input prediction was written AI-off before the run, and the actual
result is documented. The cited base SHA does not establish that the prediction was committed
before the run. Meeting the rubric's separate pre-run commit requirement would require a new
AI-off, precommitted test; this historical result is presented with that limitation.

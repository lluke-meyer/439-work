# Project 2 - Portfolio Decision Workbench

AI announcement: I used OpenAI Codex to help organize the Project 2 application, calculations, and documentation. I independently review the evidence, checks, and recommendation; the analysis and decision remain mine.

Education, not investment advice: This is a FIN 43900 course project and learning demonstration, not investment advice.

## Decision and intended user

This project supports a portfolio or quantitative analyst advising an investment committee. The
selected allocation passes the displayed portfolio controls, but the current full-process call is
**reject/redesign**: do not adopt or fund a live pilot until the reserve evidence, point-in-time
signal, costs, turnover, and holdout checks are complete.

## What the product does

The Streamlit workbench connects a constrained portfolio search with transparent allocation
baselines and a frozen signal backtest. It provides:

- a six-fund default universe with monthly adjusted-close inputs and four optional candidates;
- a 3-10 fund-slot selector, with the six-fund default preserved;
- ten six-fund starting themes, including balanced, defense, bull-market, bear-market, inflation,
  technology, global, real-assets, income/reserve, and lower-volatility themes;
- a decision-first hero and a ten-theme allocation audit that separates allocation PASS from
  full-process adoption;
- a cached public Yahoo Finance monthly adjusted-close pull with a bundled-data fallback;
- bounded objective-return and reserve-minimum controls;
- a 9% estimated-return target and 1% reserve floor for the current working mandate;
- bounded net-exposure search with up to 10% short weight and 110% gross exposure by default, plus five efficient risk levels;
- a ticker selector, maximum ticker-weight control, and two-part exposure-overlap screen;
- equal-weight and inverse-volatility baselines with visible mandate verdicts;
- a mandate-survival gate that separates the allocation PASS from the broader process evidence covering return, reserve, overlap, exposure policy, drawdown, liquidity, turnover, derivatives governance, and holdout evidence;
- a frozen one-month-lag classroom holdout with gross and net results;
- a linked signal data card and selection ledger, including the zero-lag leakage diagnostic;
- bounded signal-lag, switch-cost, and bills-return sensitivity controls;
- visible failure status when holdout net trails buy-and-hold; and
- a decision bridge that keeps classroom controls separate from final mandate approval.

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
to pull a common monthly adjusted-close history for the available tickers. The pull is cached for
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
- `backtest.py` - reusable Lab 18 development/holdout calculation used by the app.
- `prices.csv` - bundled monthly adjusted-close price history.
- `tests/` - known-answer and Streamlit smoke checks.
- `outputs/visible-output.txt` - frozen readable snapshot of the current result.
- `docs/decision-memo.md` - investment-committee recommendation and conditions.
- `docs/validation-and-ai-use.md` - sources, tests, limitations, AI-use register, and Locked Changed-Input Record.
- `docs/evidence/peyton-cold-run-rerun.md` - Peyton's first setup failure and assisted continuation; Luke's completion confirmation is in the validation record.
- `docs/signal-data-card.md` - point-in-time timing rule, signal boundaries, and tested selection ledger.
- `recording-package/manifest.md` - final links, evidence index, and freeze checklist.
- `recording-package/` - working scripts and recording guide; replace draft placeholders after the final mandate and app output are frozen.

## Data sources and boundaries

The bundled price file contains monthly adjusted-close observations for TLT, SOXX, VTI, VXUS,
FREL, and GBTC from October 2021 through September 2026. The six-fund set remains the default.
SGOV, BND, VOO, and TIP are optional modeled candidates when they are not present in an uploaded
price file; the app labels them as modeled rather than implying that their history was observed.
Yahoo Finance live mode can replace those modeled estimates with a common observed window. The
classroom signal table covers December 2024 through June 2026 and uses a one-month availability lag.

The current working mandate uses a 9% estimated annual return target before trading costs, a 1%
reserve floor, a 30% drawdown review trigger for the requested moderately risky/risky posture, a 75% liquidity floor within 10 business days, a 25% annual one-way
turnover limit, a 40% maximum long ticker weight, a 10% maximum short ticker weight, a 110% gross-exposure
ceiling, and a 60% broad-exposure overlap cap. Shorting and limited borrowing are permitted within
those bounds. Derivatives are permitted for hedging, but derivative contracts, margin, Greeks,
financing spreads, and counterparty exposure are not priced by this app and require separate review.

TLT is marked reserve eligible as a provisional model proxy. [iShares describes TLT](https://www.ishares.com/us/products/239454/ishares-20-plus-year-treasury-bond-etf)
as targeted exposure to 20-plus-year government debt; its effective duration is about 15 years, so
its price can move substantially when rates change. It is a liquid risk asset, not a cash
equivalent. A short Treasury bill fund such as [SGOV](https://www.ishares.com/us/products/314116/ishares-03-month-treasury-bond-etf)
would be a cleaner reserve candidate. SGOV is available in the selector and is treated as the
preferred reserve candidate when selected, although its status remains a modeled-data review until
an observed SGOV history is uploaded. TLT stays available as a risk-asset proxy, not cash.

The overlap screen has two layers: gross broad exposure buckets such as U.S. equity beta and long
Treasuries, plus a pairwise screen for selected active funds whose estimated correlation is at least
70%. The pairwise screen caps the combined weight at 70% by default. Neither screen replaces
holdings-level look-through.

## Current results and limitations

The default allocation passes the displayed return, reserve-floor, ticker, overlap, exposure, and
30% drawdown controls. The full process still rejects/redesigns because the frozen signal's turnover
and holdout evidence fail, while liquidity, issuer look-through, reserve evidence, and derivative
governance remain review items. The theme audit is intentionally separate: a theme can pass the
allocation controls while the full process remains reject/redesign because process evidence is unresolved.
The frozen classroom signal produces 6.13% development net and -6.09% holdout net versus -2.09%
buy-and-hold, so its failure rule triggers. The app displays that failure rather than averaging it
away.

Before submission, the remaining human-owned steps are the three recordings, corrected video
transcripts, manifest links/durations, access check, and frozen commit. Luke confirmed the partner
handoff complete; the supplied partner note does not contain a separate post-fix README-only log.
The current signal data card
and zero-lag leakage diagnostic are included in the repository; no new signal was selected after
seeing the holdout.
The mandate, final decision, derivative disclosure, and changed-input scenario are documented.
The cited base SHA does not establish that the prediction was committed before the run.

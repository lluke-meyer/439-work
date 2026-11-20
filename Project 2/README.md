AI announcement: I used OpenAI Codex to help build, test, and document this app. I take responsibility for the analysis, checks, and committee decision.

Education, not investment advice: This is a FIN 43900 course project and learning demonstration, not investment advice.

# Project 2 - Portfolio Review

## My decision

I built this app for an analyst speaking to an investment committee. I chose VOO, VTI,
VNQ, VWO, FBTC, FBND, FIVA, SGOV, TLT, and TIP as the ten-fund universe. All ten start
selected, though a fund can receive zero weight. At my working 9% return target and 10%
FBTC cap, the app finds **no feasible allocation**. I recommend **reject adoption and
redesign** because the separate timing rule fails turnover and holdout checks and the
price panel does not include cash distributions.

## What I built

I combined a constrained portfolio search, two simple allocation baselines, and a frozen
classroom signal test in one Streamlit app.

I separate two questions: whether an allocation clears the numerical limits, and whether
the evidence supports adopting the whole process. My mandate finder shows what limits a
fixed mix would need. The adjacent full-process check shows what still fails or needs
review. The equity-versus-bills classroom signal is a separate test, not the realized
return of these ETFs.

I included:

- all ten selected funds, a 3-10 fund-slot control, and ten six-fund starting themes;
- a fixed-weight mandate finder, numerical Auto-Pass with a restore button, and a
  separate full-process check that names the failed or unresolved evidence;
- bounded return, reserve, ticker, FBTC, overlap, short, gross-exposure, drawdown,
  signal-lag, trading-cost, and bills-return controls;
- equal-weight and inverse-volatility baselines, up to five feasible risk levels,
  and a ten-theme audit with visible allocation verdicts;
- a frozen Nasdaq price panel with a full or recent 24-return risk window, plus
  optional Yahoo live data and CSV upload;
- a frozen one-month-lag classroom holdout with gross/net results, a zero-lag
  leakage check, and a linked signal card and selection ledger; and
- a committee-review header, collapsible seven-step walkthrough, and verdict
  strip that stays visible while I scroll.

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

The terminal prints a local URL, normally `http://localhost:8501`.

I default to the bundled CSV. If I select **Yahoo Finance (live)**, the app pulls a common
monthly history for the available tickers. That adapter uses adjusted close when Yahoo
supplies it and otherwise uses close. I would verify the field before mixing sources or
interpreting returns. The pull is cached for one hour; if it fails or is rate-limited,
the app reports the problem and falls back to the bundled file. I would record the source,
date window, and fallback status before using any live output as evidence.

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

I also included a [default visible result](outputs/visible-output.txt) and the
[locked cap-change output](outputs/locked-changed-input-output.txt) so a grader can read
the decision and test without running the app.

## Repository map

- `app.py`, `portfolio.py`, `mandate_finder.py`, `auto_pass.py`, and
  `process_audit.py` - interface, allocation search, mandate boundaries, and
  separate numerical and full-process checks.
- `backtest.py` and `docs/signal-data-card.md` - frozen timing test and signal ledger.
- `prices.csv` and `data/` - frozen prices, source record, and preparation script.
- `tests/` and `outputs/` - checks, current output, and locked cap-change result.
- `docs/` - memo, validation and AI-use record, and Peyton's historical cold-run note.
- `recording-package/` - corrected caption text and submission manifest.

## Data sources and boundaries

My bundled file has 33 common monthly closes from January 2024 through September 2026.
I list the Nasdaq URLs, SHA-256 checksums, and transform in the [price-source record](data/prices-source.md).
These closes **exclude cash distributions**. I use price changes for volatility,
correlation, and drawdown screens; the editable annual return inputs are **illustrative
scenario assumptions**, not verified forecasts or historical total returns. I can compare
all 32 monthly returns with the most recent 24 for price-based risk estimates. A 36-return
choice appears only for longer uploaded or live panels. Changing this window does not
change my scenario return assumptions. My separate classroom signal uses a one-month lag.

My working horizon is five years, with quarterly committee review and annual core
rebalancing. I use a 9% scenario annual return target before trading costs, a 1% SGOV
reserve floor, a 30% price-drawdown review trigger, a 75% liquidity floor within ten
business days, and a 25% annual one-way turnover limit. I cap a long ticker at 40%,
FBTC at 10%, short weight at 10% per ticker, gross exposure at 110%, broad overlap at
60%, and a highly correlated pair at 70% combined weight. The app permits bounded
shorting and borrowing. Derivative hedges would need separate review because this app
does not price contracts, margin, Greeks, financing, or counterparty exposure. These
are my proposed controls, separate from the Lab 13 teaching case. The committee has
not approved them. The app screens a candidate allocation; it does not execute
annual rebalancing. My separate monthly timing rule fails turnover and holdout checks.
I framed this for a moderately risky to risky five-year mandate, not a
capital-preservation reserve. The 30% price drawdown is a stop-and-review trigger,
not a guarantee or an approved loss budget.

I count only [SGOV](https://www.ishares.com/us/products/314116/ishares-03-month-treasury-bond-etf)
as the working reserve. [TLT](https://www.ishares.com/us/products/239454/ishares-20-plus-year-treasury-bond-etf)
is optional long-duration exposure, not cash. The committee has not approved my
reserve and liquidity policy.

I screen overlap in two ways: broad gross-exposure buckets, and pairs of active funds
with at least 70% estimated correlation. The default pair cap is 70% combined weight.
Holdings-level look-through is absent, so neither screen is enough for adoption.

## Current results and limitations

At 9% target and 10% FBTC cap, I find no feasible mix. My starting equal-weight mix
supports only a 6.45% return target, although its 10% FBTC weight meets the bitcoin
cap. I show those numbers to explain the gap, not to argue for lowering policy. A 7.5%
target can produce a numerical PASS, but the full process still fails.

Numerical Auto-Pass finds the highest scenario return on the 10% weight grid under the
same reserve and risk limits: 7.75% with VOO 40%, VTI 20%, FBTC 10%, FIVA 20%, and
SGOV 10%. It applies a usable 7.7% target and lets me restore my prior inputs. I treat
this as a sensitivity, not an approved mandate. The full-process pass check lists
failures and missing evidence without changing their status. Turnover and holdout still
fail, and the price panel remains REVIEW because it excludes distributions. My classroom
timing rule returned 6.13% net in development but -6.09% net in the holdout versus
-2.09% buy-and-hold.

I pushed my AI-off prediction in `6055fcc` before the new [locked test](docs/validation-and-ai-use.md#locked-changed-input-record---november-19-2026).
Lowering the general ticker cap from 40% to 30% cut passing starting themes from three
to one, but the constrained search still returned 7.55%. The [observed output](outputs/locked-changed-input-output.txt)
records the partial match and unchanged full-process rejection. My November 15 test
remains historical because its cited SHA did not lock that earlier prediction.

My [submission manifest](recording-package/manifest.md) links the three videos and
corrected transcripts. Video 1 explains what my locked prediction got right and wrong;
the [changed-input output](outputs/locked-changed-input-output.txt) preserves both runs.
I retain Peyton's earlier partner cold run with its limits stated: it covers the old
six-fund version, and the supplied note does not show a separate post-fix README-only
rerun. I have not selected a new timing signal after seeing the holdout.

# Peyton's Project 2 cold-run note

## Scope and provenance

- Date: November 17, 2026 (EST).
- Repository link supplied: https://github.com/lluke-meyer/439-work/tree/main/Post%20Project%201/Lab%2020%20-%20for%20Peyton
- Verified commit: `813865ced5ca2e38ec33cebf0086d713ea79ce00` (Publish Project 2 app for partner cold run).
- Fresh copy: `C:\Users\Peyto\Documents\lab20-partner-rerun-20261117\source\lluke-meyer-439-work-813865c`.
- Source: a fresh ZIP downloaded from GitHub at that exact commit, separate from the earlier downloaded archive.
- Instructions used: the handoff README, then the canonical `Project 2/README.md`. Application source was not inspected or changed to obtain these results.
- Execution disclosure: Codex executed commands and operated Edge at Peyton's request. These are observed AI-assisted test results, not a claim that Peyton independently performed an AI-off exercise or that a partner conversation occurred.

## First pass — README-only result

From the fresh repository root, these README commands were attempted in Windows PowerShell:

```powershell
cd "Project 2"
python3 -m venv .venv
```

The directory change succeeded. The first setup command failed:

```text
Program 'python3.exe' failed to run: The file cannot be accessed by the systemAt line:4 char:1
+ python3 -m venv .venv
+ ~~~~~~~~~~~~~~~~~~~~~.
At line:4 char:1
+ python3 -m venv .venv
+ ~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : ResourceUnavailable: (:) [], ApplicationFailedException
    + FullyQualifiedErrorId : NativeCommandFailed
```

At the tested commit, the README labeled its instructions as Bash. This Windows machine had PowerShell and working Python 3.13.15 under `python`, but no Bash was found on PATH or at the standard Git Bash location. `python3` resolved to the WindowsApps executable alias. That README did not provide a Windows alternative. Its subsequent `source .venv/bin/activate` command was not attempted.

**README-only verdict: blocked at setup.** This is a setup/environment compatibility failure, not evidence that the portfolio calculations are wrong. The earlier failure record remains in `C:\Users\Peyto\Downloads\peyton-cold-run.md`.

## Assisted continuation — actual commands

To inspect the app beyond that failure, Codex used Windows equivalents in `Project 2/`. These substitutions were not in the README at the tested commit. Luke later added PowerShell instructions in `6782c19`.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --disable-pip-version-check --retries 0 --timeout 15
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --disable-pip-version-check --retries 0 --timeout 30
.\.venv\Scripts\python.exe -m streamlit run app.py --server.headless true --server.address 127.0.0.1 --browser.gatherUsageStats false
```

The first pip attempt ran within the tool sandbox and could not resolve a Streamlit distribution. Retrying with approved network access installed the declared dependencies successfully, including Streamlit 1.67.0. This sandbox/network issue is recorded separately from the project's setup failure. The full virtual-environment Python path replaces shell activation. The launch flags keep the server local and suppress automatic browser opening and usage reporting.

## Timing

- Fresh README review began: 2:13:36 PM EST.
- Setup failure observed: 2:14:15.936 PM EST, about 40 seconds after README review began. The failed command block took about 0.74 seconds.
- Server reported ready: 2:18:34.957 PM EST.
- First live decision observed in Edge: 2:19:59.115 PM EST.
- Elapsed to first live decision: approximately **6 minutes 23 seconds**, measured from the fresh README review, including dependency installation, tool delays, a browser-access interruption, and user assistance closing a dialog. This is not uninterrupted app computation time.
- Changed-control result verified: 2:20:33.470 PM EST.

## Live result and one bounded control change

The result appeared at `http://127.0.0.1:8501/`, in the top **Make the portfolio call** panel. Supporting results appeared in **The proposed mix**, **Baseline and mandate verdicts**, and **The frozen signal and its holdout**. The test used the bundled six-fund universe and default inputs, then changed only **Objective return (%)** from **9.00** to **10.00** and pressed Enter. Results were read after recalculation, not from the briefly stale display immediately after editing.

| Observed item | Default: objective 9% | Changed: objective 10% |
|---|---:|---:|
| Allocation mandate | PASS | PASS |
| Full process gate | REJECT / REDESIGN | REJECT / REDESIGN |
| Estimated return | 9.19% | 10.18% |
| Volatility | 15.45% | 15.94% |
| Reserve weight | 20.00% | 10.00% |
| Frozen holdout net | -6.09% | -6.09% |
| Holdout buy-and-hold | -2.09% | -2.09% |
| TLT weight | 20.00% | 10.00% |
| SOXX weight | 10.00% | 10.00% |
| VTI weight | 30.00% | 30.00% |
| VXUS weight | 40.00% | 40.00% |
| FREL weight | 0.00% | 10.00% |
| GBTC weight | 0.00% | 0.00% |

The higher objective produced a different allocation with higher estimated return and volatility. Both allocation verdicts were readable, and the full-process rejection remained visible in the page's text. The app reported annual turnover of 400% versus a 25% limit, a failed holdout comparison, and unresolved reserve, liquidity, issuer, and derivative-governance evidence. Changing the objective did not clear those process issues.

The full-process metric card truncates its text at the tested window widths; the complete `REJECT / REDESIGN` wording is present in the page's accessibility text and in the explanatory verdict farther down. No application exception was observed during this bounded UI check. No broader financial-model audit is claimed.

This is the handoff's control-operability check. It is **not** a replacement for Luke's separately required AI-off, precommitted changed-input prediction.

## Fix and rerun status

- Windows README fix: Luke added PowerShell setup and run commands in [`6782c19`](https://github.com/lluke-meyer/439-work/commit/6782c19); the original failure remains part of this cold-run record.
- Assisted continuation: app launched, both verdicts were read, and one bounded control was changed successfully, as recorded above.
- Clean README-only rerun after the fix: **not documented**. This note supports the tested six-fund run and the later README change, but it does not claim a clean post-fix partner rerun.

## Final technical validation — code kept as is

At Peyton's request, no application repairs were made. All **19 original files** in the canonical `Project 2/` directory were compared by SHA-256 with the downloaded commit archive and matched. The virtual environment and generated Python cache files are additional local runtime artifacts, not changes to those originals.

The README's validation commands were run using the same Windows virtual-environment interpreter:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -c "from backtest import run_backtest; r=run_backtest(); print(r['development']['net'], r['holdout']['net'])"
```

- **8 tests passed in 7.208 seconds**, including the app smoke test, known-answer backtest, portfolio constraints, and offline data-adapter test.
- Reproduced development net: `0.06129892046829255` (6.13%).
- Reproduced holdout net: `-0.06091537135721137` (-6.09%).
- The test runner emitted a bare-mode Streamlit `missing ScriptRunContext` warning and explicitly said it could be ignored in that mode; the app smoke test passed.
- These checks support the recorded execution results. They do not certify the financial model or resolve the app's disclosed failed/review gates.

**Disposition:** the technical cold-run attempt and assisted continuation are documented. The setup failure was fixed later in the README, but this record does not claim a clean README-only rerun or approval of Project 2.

## Code walkthrough and question

Recorded from the walkthrough notes and answer Peyton supplied on November 17, 2026.

Code location: `Project 2/portfolio.py`, lines 143–148, `expected_portfolio_return`.

- Line 143 defines `expected_portfolio_return`, which takes asset weights and expected returns and returns a number.
- Lines 144–145 convert both inputs into tuples of floating-point numbers.
- Lines 146–147 check that both tuples have the same length and raise an error if they do not.
- Line 148 uses `zip()` to pair each weight with its corresponding return, multiplies each pair, and adds the results.

**Question:** Why must the weights and returns have matching lengths and the same asset order?

**Answer supplied:** Each weight must multiply the return for the same asset. Matching lengths ensure every asset has both a weight and a return; otherwise, `zip()` would silently leave out extra entries. Matching order prevents a weight from being multiplied by another asset's return, which would produce an incorrect portfolio return. The code checks length, but it does not check asset order.

**Identified limitation:** the caller must preserve asset alignment; this function does not validate asset identity or ordering. This records a limitation, not an observed asset-order failure in the tested run. The code remains unchanged.

No GitHub push, submission, personal reflection, or author-side fix is represented as completed by this note.

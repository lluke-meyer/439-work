# Project 1 Video Recording Guide

These scripts are designed to sound spoken, not read. Use them as a tight outline, keep the webcam visible in a small corner, and preserve the screen evidence listed below. After recording, correct each transcript to match the actual audio and replace every placeholder for the URL, duration, timestamps, and frozen repository commit.

## Before recording

1. Close notifications and unrelated tabs.
2. Open the repository at its root and enlarge the text enough to read on video.
3. Start the application:

   ```bash
   cd "/Users/lukemeyer/Documents/Year 4/FA 26/FIN 439/Project 1"
   source .venv/bin/activate
   streamlit run app.py
   ```

4. Keep these items ready:
   - `docs/research-evolution.pdf`
   - `docs/decision-memo.pdf`
   - `docs/validation-and-ai-use.pdf`
   - `README.md`
   - `project1_model.py`
   - `app.py`
   - `tests/test_model.py`
   - the running Streamlit application
5. Record at 720p or better with clear audio and a small webcam view.

## Video 1 - Research Evolution and AI-Output Check

Target: 2:35-2:50. Hard stop: 3:00.

| Time | Screen evidence | Purpose |
|---|---|---|
| 0:00-0:35 | Research Evolution, Edition A | Establish the original thesis and user. |
| 0:35-1:15 | Edition B and A-to-B table | Explain the consequential change and its drivers. |
| 1:15-2:20 | Validation and AI Use, named AI-use register | Show one AI output, the independent check, and its disposition. |
| 2:20-end | Decision reconciliation | State why the evidence was sufficient and what remains qualified. |

Use `video-1-script.txt` as the spoken script. Do not read every table entry.

## Video 2 - Detailed Codebase Walkthrough

Target: 4:20-4:40. Hard stop: 5:00.

| Time | Screen evidence | Purpose |
|---|---|---|
| 0:00-0:30 | Repository root and README decision | State the decision and highest-risk claim before opening code. |
| 0:30-1:20 | README repository map, then `project1_model.py` inputs | Explain architecture and source boundaries. |
| 1:20-2:20 | `run_model`, forecast, FCFF, and valuation functions | Trace data through statements, cash flow, DCF, and bridge. |
| 2:20-2:55 | `app.py` imports and decision display | Show that the interface calls model functions rather than duplicating finance logic. |
| 2:55-3:30 | Terminal reproduction commands | Demonstrate how a clean user reproduces the frozen output and tests. |
| 3:30-4:15 | App fail-loud checkbox or terminal-growth test | Demonstrate the highest-risk boundary test. |
| 4:15-end | Acquisition overlay and limitations | Identify a material failure mode and unresolved limitation. |

Recommended terminal commands:

```bash
python project1_model.py --snapshot outputs/visible-output.txt
python -m unittest discover -s tests -v
```

Use `video-2-script.txt` as the spoken script. Show the code that matters; do not scroll through every function.

## Video 3 - Buy-Side Investment-Committee Presentation

Target: 4:35-4:50. Hard stop: 5:00. The running product should remain the main visual.

| Time | Live product evidence | Purpose |
|---|---|---|
| 0:00-0:35 | Base dashboard and committee action | Lead with watch/defer, zero allocation, price, range, and base value. |
| 0:35-0:55 | Valuation range and bridge | Defend the core value range without averaging methods. |
| 0:55-2:10 | Decision Memo page 1, external valuation table | Reconcile the conservative model with Alpha Spread and two other outside estimates; identify the margin and terminal-value differences. |
| 2:10-2:30 | Switch Base to Downside and back | Prove the action responds to calculated output. |
| 2:30-3:10 | Market-implied expectations dashboard | Show what must be true for $313.04 to work. |
| 3:10-3:50 | Semiconductor-cycle regimes | Connect the AI boom to both operating performance and beta. |
| 3:50-4:25 | Hexagon acquisition overlay | Separate strategic fit from modeled value creation. |
| 4:25-end | Monitoring rules or assumption-challenge table | State reversal conditions and end with the committee ask. |

Use `video-3-script.txt` as the spoken script. Lead with the decision, not the build process.

## After recording

- Confirm each video is separately titled and below its hard time limit.
- Upload as Unlisted or Public, never Private.
- Correct captions and transcripts for CDNS, Synopsys, Hexagon, FCFF, WACC, RPO, dollar values, percentages, and speaker attribution.
- Replace the draft timestamps with the actual evidence moments.
- Add the stable URL, exact duration, and frozen repository commit to each transcript.
- Save the corrected transcripts as `docs/transcript-video-1.txt`, `docs/transcript-video-2.txt`, and `docs/transcript-video-3.txt`.
- Confirm the memo, visible output, videos, transcripts, and validation record report the same decision and numbers.
- Transfer each final timestamp index into the 12-row Brightspace manifest.

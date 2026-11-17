# Project 2 Video Recording Guide

These scripts are designed to sound spoken, not read. Use them as tight outlines, keep the webcam
visible in a small corner, and preserve the screen evidence listed below. Replace every placeholder
for the final URL, duration, timestamps, and frozen repository commit after recording.

## Before recording

1. Open the `Project 2` repository at its root and close unrelated tabs.
2. Start the application:

   ```bash
   cd "/Users/lukemeyer/Documents/Year 4/FA 26/FIN 439"
   ./.venv/bin/python -m streamlit run "Project 2/app.py"
   ```

3. Keep these items ready:
   - `Project 2/README.md`
   - `Project 2/docs/decision-memo.md`
   - `Project 2/docs/validation-and-ai-use.md`
   - `Project 2/app.py`
   - `Project 2/portfolio.py`
   - `Project 2/market_data.py`
   - `Project 2/backtest.py`
   - the running Streamlit application
4. Record at 720p or better with clear audio and a small webcam view.

The November 15 changed-input test has no proven pre-run GitHub commit. A new human-authored,
AI-off prediction and pre-run commit are required for a complete Locked Changed-Input Record.
If you complete that test before recording, update the scripts and validation record to use the
new evidence; do not describe the November 15 test as precommitted.

## Video 1 - System Change and AI-Output Check

Target: 2:30-2:50. Hard stop: 3:00.

| Time | Screen evidence | Purpose |
|---|---|---|
| 0:00-0:15 | Required opening statements | State the AI announcement and education disclaimer in your own words. |
| 0:15-0:47 | README and decision memo | State the mandate, intended user, and current committee decision. |
| 0:47-1:27 | Lab evidence map or validation record | Explain how the system changed from the mandate and labs into one product. |
| 1:27-2:32 | Validation record and app stress | Show one AI-proposed test, the independent run, and whether the claim was accepted, qualified, corrected, or rejected. |
| 2:32-end | Decision reconciliation | State what remains provisional and what evidence would reverse the call. |

Use `video-1-script.txt` as the spoken outline. Project 2 has no Edition A or Edition B, so focus on
system evolution and the checked AI output. If you mention the November 15 changed-input run,
state that its cited SHA was not a pre-run GitHub lock.

## Video 2 - Detailed Codebase Walkthrough

Target: 4:20-4:45. Hard stop: 5:00.

| Time | Screen evidence | Purpose |
|---|---|---|
| 0:00-0:15 | Required opening statements | State the AI announcement and education disclaimer in your own words. |
| 0:15-0:42 | Repository root and README | State the decision and highest-risk claim. |
| 0:42-1:32 | Repository map, `portfolio.py`, `market_data.py`, `backtest.py` | Explain the application architecture and source boundaries. |
| 1:32-2:37 | Portfolio search and backtest functions | Trace data through estimates, constraints, lag, costs, and holdout. |
| 2:37-3:32 | `app.py` imports and visible panels | Show the decision-first hero, sidebar price source, theme selector and audit, and bounded mandate controls. |
| 3:32-4:22 | Tests and visible output | Reproduce the known-answer values and show the mandate verdict/holdout panel. |
| 4:22-end | Limitation and failure rule | Explain the reserve classification, holdout failure, or other highest-risk limitation. |

Recommended terminal command:

```bash
cd "Project 2"
../.venv/bin/python -m unittest discover -s tests -v
```

## Video 3 - Buy-Side Investment-Committee Presentation

Target: 4:30-4:50. Hard stop: 5:00. Keep the running product as the main visual.

| Time | Live product evidence | Purpose |
|---|---|---|
| 0:00-0:50 | Two required opening statements (0:00-0:15), then live app | Raise Reserve minimum from 1% to 25%, read `Allocation mandate: NO FEASIBLE MIX`, then reset to 1% and read `PASS`. |
| 0:50-1:35 | Baseline and mandate verdict table | Explain the allocation range and which rules pass or fail. |
| 1:35-2:25 | Frozen holdout panel | Show development and holdout gross/net results and the failure rule. |
| 2:25-3:25 | App decision gates and risk controls | Defend the recommendation, assumptions, costs, and monitoring triggers with the app on screen. |
| 3:25-4:20 | Reserve and exposure details | Explain the condition most likely to reverse the decision and disclose the derivative boundary. |
| 4:20-end | Committee ask | End with reject/redesign plus the conditions that would reverse the decision. |

Use `video-3-script.txt` as the spoken outline. Lead with the decision, not the build process.

## After recording

- Confirm each video is separately titled and below its hard time limit.
- Upload as Unlisted or Public, never Private.
- Correct captions and transcripts for tickers, finance terms, names, percentages, and material numbers.
- Replace draft timestamps with the actual evidence moments.
- Add the stable URL, exact duration, and frozen repository commit to each transcript.
- Save the corrected transcripts as `docs/transcript-video-1.txt` through `docs/transcript-video-3.txt`.
- Reconcile the memo, visible output, videos, transcripts, and validation record before creating the manifest.

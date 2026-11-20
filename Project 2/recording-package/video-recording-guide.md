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
   - `Project 2/mandate_finder.py`
   - `Project 2/data/prices-source.md`
   - `Project 2/market_data.py`
   - `Project 2/backtest.py`
   - the running Streamlit application
4. Record at 720p or better with clear audio and a small webcam view.

## Recording setup on this Mac

Use the installed Zoom desktop app to record locally, then upload each finished MP4 to YouTube
as **Unlisted**. Start a meeting alone, turn on the camera and microphone, share the whole screen
so both the app and code editor remain visible as you switch, and choose **Record on this Computer**.
Make a short test first and play it back to confirm readable app text, your camera thumbnail, and
clear audio. Record each of the three videos as its own session and file. Zoom's
[computer-recording guide](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0076922)
and YouTube's [visibility guide](https://support.google.com/youtube/answer/157177) cover the
current controls. Correct the YouTube captions and save a separate plain-text transcript for
each video after upload.

Complete the new human-authored, AI-off changed-input prediction and commit it before its run.
Then record the exact before/after result and update the validation record. The November 15
test remains historical; its cited SHA does not prove a pre-run lock. Do not read Video 1's
bracketed placeholder or call the new record complete until this step has happened.

## Video 1 - System Change and AI-Output Check

Target: 2:30-2:50. Hard stop: 3:00.

| Time | Screen evidence | Purpose |
|---|---|---|
| 0:00-0:15 | Required opening statements | State the AI announcement and education disclaimer in your own words. |
| 0:15-0:55 | Ten-fund selector and mandate finder | Explain the fund choice and what the new feature answers. |
| 0:55-1:30 | Validation record and SGOV/TLT source links | Explain the checked AI reserve assumption and changed classification. |
| 1:30-2:05 | Price source and data-quality gate | Explain the unadjusted-price boundary and scenario returns. |
| 2:05-2:35 | New Locked Changed-Input Record | Give Luke's own prediction, pre-run commit, result, mechanism, and decision effect. |
| 2:35-end | Decision hero and memo | State reject/redesign and reversal conditions. |

Use `video-1-script.txt` as the spoken outline. Project 2 has no Edition A or Edition B, so focus on
system evolution and the checked AI output. Keep the old and new changed-input records distinct.

## Video 2 - Detailed Codebase Walkthrough

Target: 4:20-4:45. Hard stop: 5:00.

| Time | Screen evidence | Purpose |
|---|---|---|
| 0:00-0:15 | Required opening statements | State the AI announcement and education disclaimer in your own words. |
| 0:15-0:42 | Repository root and README | State the decision and highest-risk claim. |
| 0:45-1:35 | Repository map, price source and transform | Trace the new ten-fund panel and its distribution limitation. |
| 1:35-2:25 | `portfolio.py` | Explain the return assumptions, constraints, and separate bitcoin cap. |
| 2:25-3:20 | `mandate_finder.py`, `auto_pass.py`, and app | Explain fixed-weight boundaries and the numerical Auto-Pass search. |
| 3:20-4:05 | `backtest.py`, process check, and app | Show the frozen rule, cost, lag, holdout, turnover, and why the full process cannot auto-pass. |
| 4:05-end | Tests and visible output | Show local checks, the earlier partner-run boundary, and the human work still needed. |

Recommended terminal command:

```bash
cd "Project 2"
../.venv/bin/python -m unittest discover -s tests -v
```

## Video 3 - Buy-Side Investment-Committee Presentation

Target: 4:30-4:50. Hard stop: 5:00. Keep the running product as the main visual.

| Time | Live product evidence | Purpose |
|---|---|---|
| 0:00-1:05 | Two statements, then live app | Show `NO FEASIBLE MIX` at 9%; click Auto-Pass to apply 7.7% and show numerical `PASS`, full-process `REJECT / REDESIGN`, and frozen holdout gross/net. Use the restore button. |
| 1:05-1:55 | Ten-fund selector and SGOV/FBTC controls | Defend fund roles, reserve choice, bitcoin cap, and VOO/VTI overlap. |
| 1:55-2:50 | Mandate finder | Explain the restored equal-weight return and bitcoin boundaries without endorsing weaker policy. |
| 2:50-3:40 | Data source and quality gate | Explain Close/Last versus total return and unverified assumptions. |
| 3:40-4:20 | Full-process button and holdout gates | Show the blocker list and explain turnover and after-cost holdout failure. |
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

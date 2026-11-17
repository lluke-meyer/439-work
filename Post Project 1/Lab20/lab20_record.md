# Lab 20 - Project 2 Readiness

November 17, 2026.

## D - Decision

Could a new reader reach the Project 2 decision from the repository, and would that decision
survive a changed input?

Committee call: `REJECT / REDESIGN`. The displayed allocation passes, but the frozen signal's
turnover and net holdout fail. Reconsider only after those checks pass and the reserve, liquidity,
issuer, and derivative evidence is resolved. The [Project 2 memo](../../Project%202/docs/decision-memo.md)
contains the monitoring triggers and full recommendation.

## R - Partner cold run

- Peyton tested a fresh ZIP of [commit `813865c`](https://github.com/lluke-meyer/439-work/commit/813865ced5ca2e38ec33cebf0086d713ea79ce00). His [full note](../../Project%202/docs/evidence/peyton-cold-run-rerun.md) preserves the commands, timing, results, and limitations.
- On Windows PowerShell, the README-only run stopped at `python3 -m venv .venv` about 40 seconds after he began reading. Windows resolved `python3` to an unusable WindowsApps alias; the README had only Bash steps.
- With Codex-assisted PowerShell substitutions, the app opened in Edge after about 6 minutes 23 seconds from README review. That interval includes installation and tool/browser delays. The default screen showed allocation `PASS`, full process `REJECT / REDESIGN`, 9.19% estimated return, and -6.09% frozen holdout net versus -2.09% buy-and-hold.
- Peyton changed the objective from 9.00% to 10.00%. Estimated return rose to 10.18%; the allocation remained `PASS` and the full process remained `REJECT / REDESIGN`. The frozen holdout did not change. Eight Windows tests passed in the assisted continuation.
- This was a real README setup failure followed by an AI-assisted run. It was not a clean independent README-only result. Peyton also noted that the full-process metric card truncated its text at the tested widths, while the full verdict remained readable elsewhere.

## I - Changed input and code explanation

The earlier AI-off prediction changed the objective from 9.00% to 10.50% annually. I expected
fewer theme portfolios to pass. The default six-fund allocation still passed at 10.68%, but all
ten themes returned `NO FEASIBLE MIX`; the full process decision remained `REJECT / REDESIGN`.
This matched the predicted direction under the reserve, ticker, overlap, exposure, and grid
constraints. The prediction was recorded November 15 at 6:45 PM, but the cited `44ee60e` SHA was
only the base HEAD while Project 2 was uncommitted. It does not prove a pre-run GitHub lock.
Commit `813865c` was made November 17 after the November 15 run and already contains the result,
so it also cannot serve as the pre-run commit.
Peyton's separate 9.00% to 10.00% control check is an operability test, not the locked prediction.

Peyton supplied a question on [`expected_portfolio_return`](../../Project%202/portfolio.py#L143):
why must weights and returns have matching lengths and asset order? Matching lengths prevent
`zip()` from silently dropping an unmatched value; matching order keeps each weight paired with
its asset's return. The function checks length but relies on the caller for asset alignment.
I confirmed that I explained this code to Peyton without AI. Completed during class. Peyton's
note supplies the question and answer; the first-person completion is my own confirmation.

## V - Fix and result

The first failure was a Windows setup instruction gap. The [Project 2 README](../../Project%202/README.md)
now includes PowerShell setup, run, and validation commands based on the commands that worked in
Peyton's assisted continuation. The [fix was pushed in commit `6782c19`](https://github.com/lluke-meyer/439-work/commit/6782c19c06301cf579d76198e184a55dc1057742).

On November 17, I confirmed that Peyton completed the remaining partner tasks. His supplied
note documents the first README failure and assisted continuation; it does not include separate
commands, elapsed time, or screen results for a clean post-fix README-only rerun. I treat the
partner handoff as complete on my confirmation, without claiming that the supplied note proves
an independent post-fix pass. The app code and frozen holdout were not changed to turn the failed
decision into a pass.

## E - Reflect and checkout status

The cold run exposed an operating-system gap I could not see in my local macOS run. I will keep
the optimizer and frozen holdout fixed while I finish the recording package. The decision line
remains reject/redesign until the stated reversal conditions are met.

- [x] Partner's first failure, assisted continuation, timing, and result are recorded.
- [x] The first setup failure has a README fix pushed in commit `6782c19`.
- [x] The changed-input direction, actual result, and decision effect are recorded.
- [x] The committee action and reversal condition are stated.
- [x] I confirmed Peyton completed the remaining partner tasks; a separate post-fix rerun log was not supplied.
- [ ] A pre-run GitHub commit of the earlier prediction is not established by `44ee60e`.
- [x] I explained the code to Peyton without AI. Completed during class.

This lab record is the individual checkout evidence. It does not certify Project 2 or replace its
validation file, memo, videos, transcripts, and manifest.



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

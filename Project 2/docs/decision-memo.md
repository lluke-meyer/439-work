AI announcement: I used OpenAI Codex to help build and document this Project 2 app. I must independently review the inputs, checks, and committee decision; those judgments are mine.

Education, not investment advice: This is a FIN 43900 learning demonstration, not investment advice.

# Project 2 Decision Memo - Working Draft

## Decision and committee ask

**Reject adoption and redesign.** The current 9% return objective and 10% FBTC concentration
cap produce no feasible allocation under the illustrated return assumptions. More fundamentally,
the separate frozen timing process fails its 25% annual turnover limit and net holdout benchmark.
Do not fund a live pilot by relaxing the mandate until it fits the chosen funds.

## Portfolio and intended user

The user is a portfolio analyst advising an investment committee. The proposed ten-fund
universe is VOO and VTI (U.S. equity core), VNQ (listed real estate), VWO (emerging markets),
FBTC (spot-bitcoin ETP), FBND (core bonds), FIVA (non-U.S. value), SGOV (short Treasury
reserve), TLT (optional long-duration Treasury), and TIP (inflation-protected bonds).
VOO and VTI overlap substantially; FBTC is a concentrated single-asset exposure. TLT is
never treated as cash. The app initially selects all ten funds; TLT and TIP can be removed
or receive zero weight in a proposed allocation.

The working proposal has a five-year horizon, quarterly review, annual core rebalance, a 9%
scenario return target, 1% reserve floor, 30% price-drawdown review trigger, 75% liquidity
within 10 business days, 25% annual one-way turnover limit, 40% general ticker cap, 10%
FBTC cap, 60% broad-exposure cap, and a 70% combined cap on highly correlated pairs.
Bounded shorting is limited to 10% per ticker and 110% gross exposure. Derivative hedges
require a separate contract-level review. These are analyst-proposed controls, not a
committee-approved mandate.

## Evidence and the new mandate question

The frozen [price panel](../data/prices-source.md) has 33 common month-end Nasdaq closes from
January 2024 through September 2026. It excludes cash distributions. The app uses it for
price volatility, correlation, and drawdown screens. Its annual return inputs are explicitly
illustrative and editable; the 9% hurdle is **not** verified by historical total returns.
The short sample, especially for FBTC, cannot establish a five-year forecast. The bundled
data-quality gate remains REVIEW until total-return history and return assumptions are checked.

The mandate finder takes a chosen fund mix and exact weights. It reports the maximum return
target and reserve floor that mix supports, and the minimum concentration, overlap, leverage,
shorting, and drawdown allowances it requires. For the initial equal-weight ten-fund mix,
the return boundary is 6.45%, below the 9% working target, while FBTC is exactly 10%.
The chosen mix therefore fails the current numerical mandate on the return target. These are **compatibility
boundaries**, not recommendations to weaken policy. At a 7.5% target, the constrained search
can produce a numerical allocation PASS in a sensitivity run; the frozen process decision
still rejects/redesigns. The current 9% target remains the working base.

The Auto-Pass control uses the selected funds and the same reserve, concentration, exposure,
overlap, and drawdown limits. On the current 10% grid it finds a 7.75% scenario-return mix
(VOO 40%, VTI 20%, FBTC 10%, FIVA 20%, SGOV 10%) and lowers the displayed target to 7.7%.
That makes the numerical allocation pass without loosening risk controls. It is a
scenario sensitivity, not a recommendation to replace the 9% working mandate; the full
process still fails.
The full-process pass check lists each remaining FAIL or REVIEW with the required evidence.
It cannot create a new untouched holdout, verified total-return history, or committee
approval by changing a control in the app.

The classroom equity-versus-bills signal is separate from the selected ETF mix. Its
development net result is 6.13%, but its untouched holdout is -6.09% net versus -2.09%
buy-and-hold. Four development switches represent 400% one-way turnover against the
working 25% limit. The holdout and turnover failures cannot be cured by choosing a
mandate that admits a particular fund mix.

## Action range and reversal conditions

Current action: reject adoption, preserve the 9% base and frozen signal, and authorize a
redesign. A revised proposal could be considered only after:

1. the committee approves the mandate and return assumptions using verified total-return
   history, with SGOV reserve and issuer/liquidity evidence;
2. a revised portfolio passes the numerical constraints without an undisclosed exception;
3. any proposed timing rule is frozen before a fresh holdout and meets the after-cost
   benchmark and turnover limit; and
4. derivative, holdings overlap, and issuer risk receive the necessary look-through.

Monitor the return and FBTC caps, reserve coverage, broad and pairwise overlap, price
drawdown, trading cost, turnover, and gross/net holdout result. A failed hard rule keeps
the recommendation at reject/redesign. A REVIEW item blocks adoption until its evidence
is supplied.

## Open items before freezing

- Luke must author and precommit a new AI-off changed-input prediction before its run.
- Peyton's November 17 cold run is retained as historical partner evidence for the earlier
  six-fund version. Luke will inspect this revised app and mandate finder himself; no new
  partner cold run is available, so it is not claimed for this version.
- Re-record the three videos against the final app, correct transcripts, and add actual
  links and timestamps to the manifest.

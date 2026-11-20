AI announcement: I used OpenAI Codex to help build, test, and document this app. I take responsibility for the analysis, checks, and committee decision.

Education, not investment advice: This is a FIN 43900 learning demonstration, not investment advice.

# Project 2 Decision Memo

## My recommendation

I recommend **reject adoption and redesign**. At my working 9% return target and 10% FBTC cap,
the app finds no feasible allocation under the illustrative assumptions. The separate timing
rule also fails my 25% turnover limit and the net holdout comparison. I would not fund a pilot
by relaxing the mandate to fit these funds.

## The portfolio and mandate I chose

I built this for an analyst presenting a portfolio to an investment committee. I chose
VOO and VTI for a U.S. equity core, VNQ for real estate, VWO for emerging markets,
FBTC for bitcoin, FBND for core bonds, FIVA for non-U.S. value, SGOV for a short Treasury
reserve, and TLT and TIP for optional duration and inflation-protected exposure. All ten
start selected; a fund can receive zero weight. VOO and VTI overlap, so I show that risk.
I cap FBTC separately at 10% and never count TLT as cash.

My working horizon is five years, with quarterly committee reviews and annual core
rebalancing. I set a 9% scenario return target, 1% SGOV reserve floor, 30% price-drawdown
review trigger, 75% liquidity floor within ten business days, and 25% annual one-way
turnover limit. I cap any ticker at 40%, FBTC at 10%, broad-exposure overlap at 60%, and
highly correlated pairs at 70% combined weight. The app permits up to 10% short weight
per ticker and 110% gross exposure. I would require a separate contract-level review
for any derivative hedge. These are my proposed limits; the committee has not approved them.
I framed the proposal for a moderately risky to risky five-year mandate, not a
capital-preservation reserve. The 30% price drawdown is a stop-and-review trigger,
not a guaranteed loss limit or permission to keep trading through a breach.

## What the evidence tells me

My [price panel](../data/prices-source.md) has 33 common month-end Nasdaq closes from January
2024 through September 2026. It excludes cash distributions. I use those prices for
volatility, correlation, and drawdown screens. The annual return inputs are editable
scenario assumptions, **not** forecasts verified by total-return history. The short
sample, especially for FBTC, cannot support a five-year forecast. I leave data quality
at REVIEW until I have adjusted total-return history and defensible return assumptions.
The input I would challenge first is FBTC's 12% annual scenario return. It is the
highest return assumption in the app, and I have not justified it with a reliable
five-year return record. I would not use its upside to make a weak mandate pass.

I added the mandate finder because I wanted to test a mix I chose, not just accept an
optimizer's mix. It shows the highest return target and reserve floor that exact set of
weights can meet, plus the minimum caps or tolerances it needs. My starting equal-weight
mix supports at most a 6.45% return target, below my 9% hurdle; its 10% FBTC weight meets
the separate bitcoin cap. I read that as a failed return screen, not a reason to lower
the committee's target. A 7.5% target can produce a numerical PASS, but the tested process
still fails. I keep 9% as the working base.

Numerical Auto-Pass searches only the selected funds under the same reserve and risk limits.
On the 10% weight grid it finds 7.75% scenario return with VOO 40%, VTI 20%, FBTC 10%,
FIVA 20%, and SGOV 10%, then sets a usable 7.7% target. That produces a numerical PASS.
I use it as a sensitivity check, not a recommendation to replace my 9% mandate. The
full-process pass button lists the failed and unresolved checks; it cannot turn a failed
holdout or missing evidence into a PASS.

For my [locked changed-input test](validation-and-ai-use.md#locked-changed-input-record---november-19-2026),
I committed an AI-off prediction before lowering only the general ticker cap from 40%
to 30%. My fixed mix with 40% VOO flipped from PASS to FAIL, and passing starting themes
fell from three to one. I expected return to fall, but the constrained search still
passed at 7.55% scenario return. The tighter cap changed which weights qualified;
it did not change the return assumptions or repair the process.

My classroom equity-versus-bills timing test is separate from this ETF mix. It earned
6.13% net in development, then lost 6.09% net in the untouched holdout versus a 2.09%
loss for buy-and-hold. Four development switches mean 400% one-way turnover against
my 25% limit. I cannot fix those failures by choosing a mandate that admits the mix.

## What would change my decision

I would reject adoption now, keep the 9% working base and frozen signal on record, and
redesign the proposal. I would reconsider only after:

1. I verify total-return history and justify the return assumptions, and the committee
   approves the mandate, SGOV reserve, liquidity, and issuer policy;
2. a revised allocation passes the numerical limits without a hidden exception;
3. I freeze any revised timing rule before a new holdout, and it clears the after-cost
   benchmark and turnover limit; and
4. I complete derivative and holdings-level overlap and issuer reviews.

I would monitor the return and FBTC caps, reserve coverage, overlap, price drawdown,
trading cost, turnover, and gross and net holdout results. A failed hard rule keeps my
recommendation at reject/redesign. A REVIEW item blocks adoption until I can supply
the missing evidence.

## Evidence limits

- My prediction is locked in `6055fcc`. The [validation record](validation-and-ai-use.md)
  preserves the observed result, and I explain the partial match in Video 1.
- I am keeping Peyton's November 17 cold run as evidence for the earlier six-fund version.
  I do not have a partner run of this ten-fund version.
- The [manifest](../recording-package/manifest.md) links the three recordings,
  corrected transcripts, and timestamped evidence.

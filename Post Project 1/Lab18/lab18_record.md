# Lab 18 — Legend Investor as Skill

## D — Define

Can an investor's philosophy become a skill the AI runs the same way every time — every number
computed by code from the 10-K, with the judgment left to the model?

The deliverable is a reusable Buffett-style business-quality screen. It evaluates five fiscal
years of SEC EDGAR 10-K facts, computes owner earnings and ROE, runs three fixed checks, displays
the results in Streamlit, and produces a short own/watch/pass memo without using price data.

## R — Represent

The submitted skill is [`warren-buffett-expert/SKILL.md`](warren-buffett-expert/SKILL.md). It keeps
the data rules in the skill instructions and bundles the SEC EDGAR script that supplies every
number used by the memo.

| Rule | Implementation |
|---|---|
| Filings | `form == "10-K"` only; last five fiscal years by fiscal-year-end date |
| Flow periods | One-year periods; latest filing wins for the same period |
| Revenue | `RevenueFromContractWithCustomerExcludingAssessedTax`, then `Revenues` |
| Net income | `NetIncomeLoss` |
| Operating cash flow | `NetCashProvidedByUsedInOperatingActivities` |
| Capital spending | `PaymentsToAcquirePropertyPlantAndEquipment`, then `PaymentsToAcquireProductiveAssets` |
| Equity | `StockholdersEquity` |
| Owner earnings | Operating cash flow minus capital spending |
| Missing facts | `not found`; checks without required inputs are `not known` |
| Units | USD millions; ROE is a percentage |

## I — Implement

Run the bundled SEC script for COST from the FIN 439 folder:

```bash
SEC_USER_AGENT='Luke Meyer <lmeyer@purdue.edu>' \
"Project 1/.venv/bin/python" \
"Post Project 1/Lab18/warren-buffett-expert/scripts/sec_buffett_financials.py" COST
```

Run the Streamlit app:

```bash
SEC_USER_AGENT='Luke Meyer <lmeyer@purdue.edu>' \
"Project 1/.venv/bin/streamlit" run "Post Project 1/Lab18/app.py"
```

Code links:

- [`SKILL.md`](warren-buffett-expert/SKILL.md#L8-L42) — reusable workflow and data rules.
- [`sec_buffett_financials.py`](warren-buffett-expert/scripts/sec_buffett_financials.py#L13-L47) — SEC endpoints and User-Agent.
- [`sec_buffett_financials.py`](warren-buffett-expert/scripts/sec_buffett_financials.py#L63-L126) — 10-K filtering and latest-filing selection.
- [`sec_buffett_financials.py`](warren-buffett-expert/scripts/sec_buffett_financials.py#L142-L213) — five-year rows, owner earnings, and ROE.
- [`sec_buffett_financials.py`](warren-buffett-expert/scripts/sec_buffett_financials.py#L216-L235) — the three Buffett checks.
- [`app.py`](app.py#L38-L72) — printed-number extraction and memo flags.
- [`app.py`](app.py#L75-L94) — memo generation from the script report.
- [`app.py`](app.py#L107-L146) — table, checks, chart, memo, and validation message.
- [`cost_memo.md`](cost_memo.md) — COST memo using only printed script numbers.
- [`public_research.py`](public_research.py#L1-L101) — dated analyst, valuation, and news snapshot.
- [`app.py`](app.py#L247-L390) — Buffett Test Plus overlay and decision bridge.
- [`technical_analysis.py`](technical_analysis.py#L17-L55) — public daily-history request and input validation.
- [`technical_analysis.py`](technical_analysis.py#L58-L110) — moving averages, momentum, RSI, and trend rules.
- [`technical_analysis.py`](technical_analysis.py#L113-L196) — technical snapshot and check table.
- [`app.py`](app.py#L260-L307) — technical panel, chart, caching, and formulas.
- [`public_discourse.py`](public_discourse.py#L56-L129) — live Yahoo Finance news retrieval, ticker filtering, and transparent headline screen.
- [`app.py`](app.py#L392-L415) — live public-discourse panel and source-linked headline expanders.
- [`app.py`](app.py#L125-L205) — original and revised memo generation.

Relevant sources:

- [Lab 18 — Legend Investor as Skill](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-18-legend-investor-as-skill.md)
- [Buffett's FAskills page](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md)
- [SEC company ticker file](https://www.sec.gov/files/company_tickers.json)
- [SEC companyfacts endpoint](https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json)
- [StockAnalysis analyst consensus](https://stockanalysis.com/stocks/cost/forecast/)
- [MarketBeat analyst rating mix](https://www.marketbeat.com/stocks/NASDAQ/COST/forecast/)
- [StocksXray fair-value models](https://www.stocksxray.com/us/cost)
- [MiniValuator DCF](https://minivaluator.com/dcf/cost)
- [ValueInvesting.io intrinsic-value model](https://valueinvesting.io/COST/valuation/intrinsic-value)
- [Costco fiscal 2026 operating results](https://investor.costco.com/news/news-details/2026/Costco-Wholesale-Corporation-Reports-Fourth-Quarter-and-Fiscal-Year-2026-Operating-Results/default.aspx)
- [S&P Global Costco earnings analysis](https://www.spglobal.com/market-intelligence/en/news-insights/research/2026/10/behind-the-earnings-call-costco-q4-2026)
- [Axios tariff-cost reporting](https://www.axios.com/2026/03/05/costco-earnings-tariff-refunds)
- [Yahoo Finance COST price history](https://finance.yahoo.com/quote/COST/history/)
- [Yahoo Finance public news search](https://finance.yahoo.com/quote/COST/news/)

## V — Validate

The COST run matched the assignment's known answer in USD millions:

| Fiscal year end | Revenue | Net income | Operating cash flow | Capital spending | Equity | ROE % | Owner earnings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022-08-28 | 226,954 | 5,844 | 7,392 | 3,891 | 20,642 | 28.3 | 3,501 |
| 2023-09-03 | 242,290 | 6,292 | 11,068 | 4,323 | 25,058 | 25.1 | 6,745 |
| 2024-09-01 | 254,453 | 7,367 | 11,339 | 4,710 | 23,622 | 31.2 | 6,629 |
| 2025-08-31 | 275,235 | 8,099 | 13,335 | 5,498 | 29,164 | 27.8 | 7,837 |
| 2026-08-30 | 303,154 | 9,226 | 15,817 | 6,435 | 35,803 | 25.8 | 9,382 |

All three COST checks passed:

- ROE of 15% or more every year: pass.
- Owner earnings positive every year: pass.
- Owner earnings grew, first year to last: pass.

The JPM probe also passed. The script printed `capital spending: not found`, owner earnings as
`not found` for every year, and `not known` for both owner-earnings checks. The ROE check remained
computable and failed because not every JPM year cleared 15%.

The Streamlit `AppTest` completed with zero exceptions and zero displayed errors after the COST
run. It rendered one five-year table, one chart, one memo text area, and the success message that
every number in the generated memo appeared in the script's printed report. The hand-typed-number
probe also passed: adding `40.0%` to the COST memo produced the error `Numbers not printed by the
script: 40.0%`.

### Buffett Test Plus

The app adds a separate, dated public-source overlay for COST retrieved on November 3, 2026. It
does not alter or average into the SEC-only Buffett checks.

| Evidence | Snapshot | Read |
|---|---|---|
| Analysts | 41 analysts; Buy consensus; $1,068 average target; $770–$1,315 range; 4.51% implied upside. A separate MarketBeat snapshot shows 1 Strong Buy, 24 Buy, 8 Hold, and 1 Sell. | Positive, but modest upside at the snapshot price; provider counts differ |
| Public valuation models | StocksXray $801; MiniValuator $718.93; ValueInvesting.io $1,800.81 | Mixed and highly model-dependent; two of three are below the snapshot price |
| Economic/news evidence | Fiscal 2026 sales +10.1%; digital comparable sales +20.7%; membership fees $5.907 billion; renewal rates 92.3% U.S./Canada and 89.8% worldwide | Strong demand, membership economics, and scale; tariff absorption/rebates remain a margin risk |

The resulting bridge is **quality confirmed; valuation caution**. The original Buffett test supports
Costco as a high-quality business, while the extra evidence supports keeping that business-quality
verdict but requiring a better price or stronger valuation evidence before treating it as a purchase
decision.

### Technical 30/60-Day Checks

The technical panel uses Yahoo Finance daily chart history, caches the result for 15 minutes, and
keeps the calculations separate from the Buffett and valuation judgments. The November 3, 2026 COST
run used 252 daily observations:

| Check | Reading |
|---|---|
| Latest close | $1,025.62 |
| 30-day SMA | $964.71 |
| 60-day SMA | $947.56 |
| 30-day momentum | +14.03% |
| 60-day momentum | +7.65% |
| RSI (14) | 63.8 — neutral |
| Combined technical label | Bullish trend |

The label requires price above both averages, the 30-day average above the 60-day average, and
positive 30- and 60-day momentum. If those conditions disagree, the app reports **Mixed trend**;
it does not force a bullish or bearish conclusion. A JPM helper run returned **Mixed trend**, which
also confirms the technical overlay is not hard-coded to COST.

### Public discourse and two-memo handoff

The app now queries Yahoo Finance's public news search for the selected ticker, filters for headlines
whose related-ticker metadata includes that ticker when available, and shows up to eight source-linked
headlines. Each headline receives a transparent keyword screen of **Supportive**, **Mixed**, or
**Caution**. The app labels this method clearly; it is not presented as a language-model sentiment
score or as intrinsic-value evidence.

The memo area now shows both versions at once:

1. **Original Buffett memo** — SEC EDGAR facts and the three original checks only.
2. **Revised Buffett Test Plus memo** — the original checks plus curated analyst/valuation evidence
   when available, live public discourse, and the technical snapshot.

The revised memo keeps the evidence layers separate and ends with a decision bridge rather than
turning public headlines or technical momentum into a standalone buy signal.

## E — Evolve

The skill is reusable for another ticker without changing the SEC data rules. The Buffett Test Plus
overlay is intentionally a dated COST snapshot: analyst targets, valuation models, and news should
be refreshed before relying on the extra evidence. A future extension can add another ticker only
after collecting an equally source-linked snapshot rather than inferring one from COST.

## R — Reflect

The code makes the repeatable part explicit: it selects only 10-K facts, keeps one-year flow
periods, preserves missing data instead of estimating it, computes owner earnings and ROE, and
evaluates the same three checks for every ticker. The model's role is the business-quality judgment
in the memo. For COST, the draft call is to **own the business** as a business-quality case because
all three checks pass and owner earnings rise from 3,501 to 9,382. This is not a price or intrinsic-

The Plus overlay adds the missing price-and-context distinction: strong operating evidence does not
automatically create a margin of safety. The analyst consensus is positive, but the valuation sources
disagree sharply, so the combined read is quality confirmed; valuation caution.



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

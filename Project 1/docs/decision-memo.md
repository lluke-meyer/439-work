# Cadence Design Systems Decision Memo

**To:** Buy-Side Investment Committee

**From:** Luke Meyer, Junior Financial Analyst

**Valuation date:** September 1, 2026

**Subject:** Defer a CDNS position at $313.04

## Decision and committee ask

I recommend **watch/defer with no position** in Cadence Design Systems at the September 1, 2026 closing price of **$313.04 per share**. The integrated FCFF DCF supports **$57.20-$111.52 per share**, including a base value of **$83.34**. Synopsys cross-checks are higher at **$189.64** from EV/TTM revenue and **$209.47** from P/E, but both remain below the market. The methods disagree on the size of the overvaluation, not on the action.

Reopen the decision only when an acquisition-aware DCF and at least two qualified peer observations independently support value at least **15% above the then-current market price**. A lower price alone is not enough; the operating evidence must also survive the next two quarterly filings.

## Evidence and as-of date

### Internal valuation map: three methods, one conclusion

| Evidence route | Implied CDNS value | Discount to $313.04 | Decision use |
|---|---:|---:|---|
| Integrated FCFF DCF | $57.20-$111.52 | 64.4%-81.7% | Primary intrinsic-value range |
| Synopsys EV/TTM revenue | $189.64 | 39.4% | Operating-value cross-check |
| Synopsys P/E | $209.47 | 33.1% | Equity-value cross-check |

I do not average the spread. The DCF prices Cadence's forecast cash flows; the peer methods show what one qualified comparable commands in the market. Synopsys remains imperfect after its Ansys acquisition, so the multiples corroborate the DCF instead of replacing it. All three methods still point to **no current entry**.

Cadence has real momentum behind it. Recurring revenue represented **80% of FY2025 revenue**. In Q2 2026, revenue reached **$1.584 billion**, backlog hit a record **$8.1 billion**, and management raised its full-year revenue-growth outlook to roughly **19%**. The broader semiconductor boom supports that strength: the Semiconductor Industry Association reported that global semiconductor sales increased **35.1% from Q1 to Q2 2026**. These results support near-term demand for Cadence's design software, hardware, and IP. They do not justify carrying boom-level growth into perpetuity.

The base forecast grows revenue from **$5.30 billion in FY2025 to $8.44 billion in FY2030**, but **74.1% of base enterprise value comes from terminal value**. Reaching $313.04 requires either adding **32.215 percentage points** to every annual growth assumption or lowering WACC to **4.871%** with base operations. Even a bounded challenge combining faster growth, a 90% gross margin, expense leverage, an 8% WACC, and 4% terminal growth reaches only **$203.95**. I do not believe the current boom closes that gap.

### External valuation reconciliation: post-date audit only

The following estimates were published or retrieved after September 1, so they are **not inputs to the dated recommendation**. They are an outside challenge to the model and a useful test of whether my conservative result is an outlier for explainable reasons.

| Outside estimate | Value per share | Method and main driver | Compared with $313.04 |
|---|---:|---|---:|
| [ValueInvesting.io](https://www.valueinvesting.io/CDNS/valuation/intrinsic-value), September 11 | $137.37 | Five-year growth-exit DCF | 56.1% below |
| [Fair Value Calculator](https://www.fairvalue-calculator.com/stock/CDNS), September 17 | $224.24 | Weighted blend of 26 models | 28.4% below |
| [Alpha Spread](https://www.alphaspread.com/security/nasdaq/cdns/dcf-valuation), retrieved October 18 | $272.92 | Seven-year FCFE with a 29.1x terminal P/E | 12.8% below |

Alpha Spread is the optimistic boundary, not evidence that one calculation is simply wrong. Its published case uses approximately **10.3% revenue growth**, net margin moving from **35.4% to 34.0%**, **101% cash conversion**, a **9.3% discount rate**, and a **29.1x terminal P/E** over seven years. Applying those assumptions to roughly **$5.838 billion** of starting revenue reproduces about **$277.46 per share**, close to Alpha Spread's $272.92. My model is deliberately more conservative: five years of accounting-linked FCFF, a 10.0% WACC, 3.0% perpetual growth, and net margins that reach roughly 20%. The gap is mainly the margin and terminal-value philosophy, not a hidden arithmetic difference. The outside estimates still remain below $313.04, while the $137-$224 observations sit much closer to my $190-$209 market cross-checks than to the traded price.

## How WACC and enterprise value were built

The sourced WACC is **10.0%**, rounded from **10.0115%**. A 4.79% ten-year Treasury yield, 4.23% implied equity risk premium, and 1.2482 industry unlevered beta produce a **1.2751 relevered beta** and **10.1837% cost of equity**. With **97.2013% equity**, **2.7987% debt**, a 5.3804% pre-tax debt cost, and a 25.1084% tax rate:

`WACC = 97.2013% x 10.1837% + 2.7987% x 5.3804% x (1 - 25.1084%) = 10.0115%`

The peer bridge is equally reproducible: Synopsys's **$85.924 billion** enterprise value divided by **$9.416 billion** of TTM revenue gives **9.1249x EV/revenue**. Applied to Cadence's **$5.838 billion** of TTM revenue, then bridged through cash, debt, and 275.393 million shares, it produces **$189.64 per share**.

## Material assumptions and sensitivities

- **Operating path:** Base revenue growth fades from 14% to 5%, gross margin is 86.5%, and operating expenses decline from 67% to 65% of gross profit. These are my analyst assumptions, not company guidance.
- **Valuation range:** Downside uses slower growth, 84.5% gross margin, 11% WACC, and 2.5% terminal growth. Upside uses faster growth, 87.5% gross margin, and 9% WACC. All accounting and cash-flow checks pass.
- **Decision rule:** Initiate requires intrinsic value at least 15% above market. Values below market but above the independently modeled **$57.20 downside value** remain watch/defer; values at or below that floor are do not initiate. Any failed model-integrity check stops the decision. The 15% hurdle is a disclosed committee-policy threshold; the lower boundary comes from the downside model.
- **Bridge boundary:** The integrated DCF retains FY2025 opening balances. The EV/revenue cross-check uses June 2026 cash, debt, and shares. I keep the bridges separate because silently inserting post-acquisition balance-sheet values into the older operating forecast would create false precision.
- **Peer boundary:** Synopsys is the only admitted public peer. Its Ansys acquisition makes it useful but imperfect, so the multiple is corroboration rather than the primary valuation.
- **Semiconductor cycle:** I now move operating performance and market risk together. An extended AI buildout adds three points to annual growth and improves margins, but a 1.35 beta lifts WACC to 10.319%; value reaches **$93.48**, not the market price. Orderly normalization produces **$83.20** at a 10.011% calculated WACC. A cycle reversal combines slower growth, margin pressure, and a 1.50 beta; value falls to **$54.69** and the decision becomes do not initiate.
- **Acquisition overlay:** Cadence completed the Hexagon D&E acquisition on February 23, 2026 for **$3.101 billion**, including **$2.2 billion cash** and **3.224 million shares**. After $154.6 million of acquired cash, net consideration was **$2.946 billion**. The filing reported $2.147 billion of goodwill and $1.248 billion of acquired intangibles. My separate default overlay uses a filing-derived $440 million starting-revenue estimate plus explicit margin, synergy, integration, reinvestment, and 10.5% WACC assumptions. It values the acquired operation at **$1.095 billion** and produces an illustrative combined value of **$78.93 per share**, or **$4.41 below** the standalone base. This is an acquisition-economics stress, not a full purchase-accounting rebuild or company guidance.

## The burden of proof

The strongest evidence is not any single price target. Rather, it is the consistency of the decision across an accounting-linked DCF, two differently defined peer multiples, a reverse DCF, and a rate sensitivity. For $313.04 to work, several separate checks would need to be wrong in the same direction.

| Evidence I trust now | Remaining uncertainty | Evidence required to reverse |
|---|---|---|
| Statements articulate; cash flow ties; scenario order and rate direction pass; the 10.0% WACC is sourced; the separate Hexagon overlay is reproducible. | The overlay is not a full post-acquisition statement rebuild and its operating inputs remain analyst assumptions. | Two filings separating acquired and organic growth, margins, integration cash costs, and reinvestment, followed by rebuilt statements and FCFF. |
| Both peer methods remain below market even though they value different claims. | Synopsys is a single peer and its Ansys acquisition changes the comparison. | At least two qualified peers admitted under the same predeclared policy and definitions. |
| The current price requires a 32.215-point annual growth shift or a 4.871% WACC; the bounded challenge reaches only $203.95. | Market-implied tests identify the burden embedded in price; they do not prove the required outcomes are impossible. | Two filings showing durable organic growth, margin realization, and cash conversion sufficient to support the revised forecast. |

## Principal risks, failure conditions, and monitoring triggers

| What could change the decision | Monitor and frequency | Committee response |
|---|---|---|
| Hexagon integration lifts durable cash flow beyond the current overlay | Analyst updates organic/acquired growth, margins, synergies, integration cash costs, FCFF, cash, debt, and diluted shares within five trading days of each 10-Q or 10-K | Replace the overlay with rebuilt statements and rerun all scenarios before reconsidering |
| Semiconductor and AI demand either accelerates or cools | Track SIA sales, backlog, RPO, guidance, customer R&D commentary, and the industry beta each quarter | Give the boom credit only when growth converts to FCFF; move toward downside if growth weakens while beta or WACC rises |
| Market expectations reset without operating damage | Track price, WACC, recurring revenue, RPO, and customer R&D commentary quarterly | Reopen only if the updated base valuation and peer evidence both clear the 15% margin-of-safety rule |
| Downside becomes more likely | Compare reported growth and gross margin with the 11%-to-2% growth path and 84.5% downside margin | Move from watch/defer to do not initiate if weaker operations persist for two filings |
| Model or evidence loses integrity | Re-run statement ties, cash-flow ties, scenario ordering, source dates, and the terminal-growth-below-WACC test after every material update | Stop and escalate if statements do not tie, a bridge is incomplete, or terminal growth reaches WACC |

## Action requested and next review point

Approve **watch/defer and zero allocation** at $313.04. Assign the analyst to refresh the DCF, peer set, and bridge after the next two quarterly filings, with an immediate recheck after a material acquisition update, financing change, or a **100-basis-point move in WACC**. Return to committee only with reconciled acquisition-aware cash flows, current peer evidence, and a price that passes the 15% margin-of-safety rule.

## Source and validation note

Material decision inputs are dated to information available by September 1, 2026. Sources include Cadence and Synopsys filings, Cadence's [Q2 2026 earnings release](https://www.sec.gov/Archives/edgar/data/813672/000081367226000089/cdns07272026ex9901.htm), the [Semiconductor Industry Association's August 6 update](https://www.semiconductors.org/global-semiconductor-sales-increase-35-1-from-q1-2026-to-q2-2026/), dated prices, U.S. Treasury rates, and Damodaran datasets. The later third-party values are labeled as a post-date audit and were not used to set the September 1 recommendation. Full tests, limitations, and named AI uses appear in **Validation and AI Use**.

This memo was prepared for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research or financial advice. The judgments and recommendation remain mine.

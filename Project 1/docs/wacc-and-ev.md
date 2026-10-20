# WACC and Enterprise-Value Evidence

**Cadence Design Systems (NASDAQ: CDNS)**

**Valuation date:** September 1, 2026

**Status:** Internal working paper; not a Brightspace deliverable.

**Purpose:** Preserve the source record for the WACC and enterprise-value peer multiple used in the submitted materials.

## Conclusion

- **Sourced WACC:** **10.0%**, rounded from 10.0115%.
- **Enterprise-value multiple:** Synopsys EV/TTM revenue of **9.1249x**.
- **CDNS value from that multiple:** **$189.64 per share**.
- **Decision effect:** Both results support **watch/defer** at the September 1 CDNS closing price of **$313.04**.

The WACC replaces the model's unsupported 9.0% base assumption. The EV result is a single-peer reference, not a stand-alone target or something to average mechanically with the DCF and P/E results.

## WACC

### Method

I used market-value capital weights and CAPM:

`Cost of equity = risk-free rate + levered beta x equity risk premium`

`WACC = equity weight x cost of equity + debt weight x pre-tax debt cost x (1 - tax rate)`

### Inputs

| Input | Value | As-of date and definition | Source |
|---|---:|---|---|
| Risk-free rate | 4.79% | September 1, 2026 U.S. Treasury 10-year par yield. I used a long-term rate because the DCF includes a terminal value. | [U.S. Treasury daily rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026) |
| Equity risk premium | 4.23% | Implied U.S. equity risk premium at the end of 2025. This was the latest annual Damodaran estimate available before the valuation date. | [Damodaran historical implied premiums](https://pages.stern.nyu.edu/~adamodar/pc/datasets/histimpl.xls) |
| Unlevered beta | 1.2482 | January 5, 2026 Software (System & Application) industry beta, corrected for cash. I used an industry beta because it is transparent and less dependent on one provider's regression choices. | [Damodaran industry betas](https://pages.stern.nyu.edu/~adamodar/pc/datasets/betas.xls) |
| CDNS market price | $313.04 | September 1, 2026 closing price. | [ChartExchange CDNS history](https://chartexchange.com/symbol/nasdaq-cdns/historical/) |
| CDNS shares | 275.393 million | Common shares outstanding at June 30, 2026. This is used for market-value capital weights, not as a forecast diluted-share count. | [Cadence Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/813672/000081367226000092/cdns-20260630.htm) |
| CDNS debt | $2,482.200 million | Unsecured long-term debt at June 30, 2026. | Cadence Q2 2026 Form 10-Q |
| Pre-tax debt cost | 5.3804% | Annualized first-half 2026 interest expense of $66.749 million divided by average debt of $2,481.175 million. | Cadence Q2 2026 Form 10-Q |
| Tax rate | 25.1084% | First-half 2026 income-tax expense of $235.601 million divided by pretax income of $938.337 million. | Cadence Q2 2026 Form 10-Q |

### Calculation

CDNS market equity equals **$86,209.025 million**:

`$313.04 x 275.393 million shares = $86,209.025 million`

The target relevered beta equals **1.2751**:

`1.2482 x [1 + (1 - 25.1084%) x ($2,482.200 / $86,209.025)] = 1.2751`

The cost of equity equals **10.1837%**:

`4.79% + 1.2751 x 4.23% = 10.1837%`

The capital weights are **97.2013% equity** and **2.7987% debt**. The resulting WACC is:

`97.2013% x 10.1837% + 2.7987% x 5.3804% x (1 - 25.1084%) = 10.0115%`

### WACC judgment

I will use **10.0%** as the base WACC. Cadence is financed mainly with equity, so the result is driven much more by the cost of equity than the cost of debt. The current 9.0% model input is no longer the best-supported base assumption.

The debt-cost estimate is a practical recent-cost proxy. It may include financing fees and intra-period borrowing changes, but debt is less than 3% of market capital, so this limitation has little effect on total WACC.

## Enterprise-value peer multiple

### Peer policy and multiple choice

Synopsys remains the admitted peer because its EDA, semiconductor-IP, verification, and engineering-software operations are the closest public comparison to Cadence. Siemens EDA remains excluded because it does not have a separately traded share price or standalone financial statements.

I used **EV/TTM revenue**. Both firms report positive revenue, and the definition can be reproduced from market prices and SEC filings. Synopsys's Ansys acquisition makes its current earnings and amortization less comparable, so an acquisition-period EV/EBITDA multiple would require more normalization than this project can defend.

### Synopsys calculation

| Input | Value | As-of date and definition | Source |
|---|---:|---|---|
| SNPS closing price | $414.82 | September 1, 2026 closing price. | [ChartExchange SNPS history](https://chartexchange.com/symbol/nasdaq-snps/historical/) |
| Common shares outstanding | 191.636646 million | August 24, 2026 shares outstanding. | [Synopsys Q3 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/883241/000088324126000025/snps-20260731.htm) |
| Cash and short-term investments | $3,607.669 million | July 31, 2026 cash, cash equivalents, and short-term investments. | Synopsys Q3 2026 Form 10-Q |
| Total debt | $10,037.360 million | July 31, 2026 current and noncurrent long-term debt. | Synopsys Q3 2026 Form 10-Q |
| FY2025 revenue | $7,054.178 million | Fiscal year ended October 31, 2025. | [Synopsys FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/883241/000088324125000028/snps-20251031.htm) |
| Nine-month FY2026 revenue | $7,161.605 million | Nine months ended July 31, 2026. | Synopsys Q3 2026 Form 10-Q |
| Nine-month FY2025 revenue | $4,799.318 million | Comparative nine-month period removed from FY2025 revenue. | Synopsys Q3 2026 Form 10-Q |

Synopsys market capitalization equals **$79,494.713 million**:

`$414.82 x 191.636646 million shares = $79,494.713 million`

Synopsys enterprise value equals **$85,924.404 million**:

`$79,494.713 + $10,037.360 - $3,607.669 = $85,924.404 million`

Synopsys TTM revenue equals **$9,416.465 million**:

`$7,054.178 + $7,161.605 - $4,799.318 = $9,416.465 million`

The peer multiple is therefore **9.1249x EV/TTM revenue**:

`$85,924.404 / $9,416.465 = 9.1249x`

### Application to CDNS

CDNS TTM revenue through June 30, 2026 equals **$5,837.623 million**:

`FY2025 revenue $5,296.759 + H1 2026 revenue $3,058.671 - H1 2025 revenue $2,517.807 = $5,837.623 million`

Sources: [Cadence FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/813672/000081367226000016/cdns-20251231.htm) and [Cadence Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/813672/000081367226000092/cdns-20260630.htm).

Applying the peer multiple produces enterprise value of **$53,267.790 million**:

`9.1249x x $5,837.623 = $53,267.790 million`

Using Cadence's June 30, 2026 bridge inputs gives equity value of **$52,226.033 million**:

`$53,267.790 + $1,440.443 cash - $2,482.200 debt = $52,226.033 million`

Using 275.393 million shares, the implied value is **$189.64 per share**:

`$52,226.033 / 275.393 = $189.64 per share`

At $313.04, CDNS itself traded at approximately **14.95x EV/TTM revenue**, a **63.8% premium** to the Synopsys reference multiple.

## Reconciliation and limits

- The **$189.64** EV/revenue result is below the market price but above the current DCF outputs. This is disagreement to explain, not a reason to average the methods.
- The peer result also remains below the existing **$209.47** Synopsys P/E reference. The two multiples use different denominators and are not expected to match.
- Synopsys is still only one peer, and its Ansys acquisition changes its product mix, leverage, shares, and revenue. I treat the result as a qualified cross-check.
- The EV calculation uses the latest filings available before September 1, 2026. The current DCF still begins with FY2025 balances. Its bridge should not be silently replaced without also making the operating forecast acquisition-aware.
- The 10.0% WACC and EV/revenue cross-check were propagated to the model, visible output, research-evolution document, and validation record before drafting the decision memo.

---

This report was prepared for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research or financial advice. AI assisted with source gathering, calculation, and drafting; the sources and final judgment remain subject to my review.

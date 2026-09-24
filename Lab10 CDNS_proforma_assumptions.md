# Cadence Design Systems (CDNS) — Lab 10 pro-forma support
All dollar figures are USD millions unless stated otherwise. The forecast file is `CDNS_proforma.py`; it uses FY2025 as the opening year and projects FY2026–FY2030.
### D — The question
**What are five years of Cadence Design Systems' statements worth, built from assumptions I can defend?**
Cadence's company-specific line is deferred revenue. Unlike ABG's inventory floor-plan financing, Cadence collects or bills some customer consideration before recognizing the related revenue, so the model links deferred revenue to projected revenue as an operating liability.
### R — History and assumptions
#### History grid
| Item | FY2023 | FY2024 | FY2025 | Filing / locator |
|---|---:|---:|---:|---|
| Revenue | 4,090.0 | 4,641.3 | 5,296.8 | 2025 10-K, Income Statements, p. 59 / lines 2061–72 |
| Gross profit | 3,655.0 | 3,993.8 | 4,574.5 | Calculated: revenue less cost of product/maintenance and services; 2025 10-K p. 59 / lines 2072–75 |
| SG&A / operating expenses* | 2,392.1 | 2,643.0 | 3,082.5 | Calculated from operating-cost lines; 2025 10-K p. 59 / lines 2076–82 |
| Net income | 1,041.1 | 1,055.5 | 1,108.9 | 2025 10-K, Income Statements, p. 59 / lines 2086–88 |
| Inventory | 181.7 | 257.7 | 303.5 | 2024 10-K, Balance Sheets, p. 53 / lines 1880–85; 2025 10-K p. 58 / lines 2020–25 |
| PP&E, net | 403.2 | 458.2 | 517.0 | Same balance-sheet locators as inventory |
| Stockholders' equity | 3,404.3 | 4,673.6 | 5,474.2 | 2024 10-K p. 53 / lines 1904–11; 2025 10-K p. 58 / lines 2043–50 |
\*The lab's SG&A line is modelled as total operating expenses after cost of revenue: marketing and sales, R&D, G&A, acquired-intangible amortization, contingent-liability loss, and restructuring. Cadence does not report a single consolidated SG&A line.
#### Ratios and operating facts
| Ratio / metric | FY2023 | FY2024 | FY2025 | Calculation / source |
|---|---:|---:|---:|---|
| Revenue growth | 14.8% | 13.5% | 14.1% | Revenue history above |
| Gross margin | 89.4% | 86.0% | 86.4% | Gross profit ÷ revenue |
| Operating expenses ÷ gross profit | 65.4% | 66.2% | 67.4% | Operating-expense definition above ÷ gross profit |
| Inventory days | 152.5 | 145.3 | 153.5 | Inventory ÷ cost of revenue × 365 |
| PP&E depreciation ÷ year-end PP&E | 19.4% | 21.2% | 21.5% | 78.4 ÷ 403.2; 96.9 ÷ 458.2; 111.4 ÷ 517.0. 2025 10-K Note 2, p. 64 / lines 2307–19 |
| Capital spending | 102.3 | 142.5 | 141.9 | PP&E purchases, 2025 10-K Cash Flows, p. 62 / lines 2203–08 |
| Effective tax rate | 18.8% | 24.4% | 27.1% | Provision ÷ pretax income; 2025 10-K p. 59 / lines 2083–88 |
| Organic / same-store growth | unresolved | unresolved | unresolved | Cadence reports total revenue; no same-store or organic growth metric was located in the cited 10-Ks. |
#### Assumption set
| Value | Label | Reason |
|---|---|---|
| Revenue growth: 14%, 12%, 10%, 8%, 5% | judgment | FY2025 total revenue grew 14.1%. I fade that rate over five years rather than assume a mature software-and-services business sustains its latest pace indefinitely. |
| Gross margin: 86.5% | history / judgment | The FY2023–25 range is 86.0%–89.4%. I use a level close to FY2025, without assuming a return to FY2023's higher mix. |
| Operating expenses ÷ gross profit: 67.0% to 65.0% | judgment | FY2025 was 67.4%, with R&D the largest expense. I assume modest scale benefits but retain heavy R&D investment. |
| PP&E depreciation: 111.4 ÷ 517.0 = 21.5% | history | FY2025 PP&E depreciation and year-end PP&E. |
| Capital spending: 142.0 annually | history / judgment | It rounds FY2024–25 PP&E purchases, which were both about $142 million. |
| Tax rate: 27.0% | guidance | Management said it expects approximately a 27% FY2026 effective tax rate (2025 10-K MD&A, p. 45 / lines 1601–03). |
| Inventory days: 153.5 | history | FY2025 inventory ÷ FY2025 cost of revenue × 365. |
| Deferred revenue: 17.64% of revenue | history / judgment | 2025 deferred revenue was $934.4m, or 17.64% of revenue. It is Cadence's company-specific operating-liability line and replaces ABG's floor-plan borrowing. |
| Other assets and other liabilities: flat | judgment | This is a transparent simplification: the opening balance sheet contains goodwill, acquired intangibles, deferred taxes, leases, receivables and accruals that are not separately forecast in this first-pass model. |
| Term debt repayment: 0 | judgment | The model assumes no scheduled principal repayment during the explicit period; it should be revised if a debt-maturity or refinancing forecast is added. |
| Share repurchase: 900 annually | judgment | FY2025 repurchases were $925.0m. I round modestly below that recent amount rather than extrapolate a larger buyback. |
| Term-debt interest: 4.71% | history | FY2025 interest expense $116.5m ÷ FY2024 long-term debt $2,476.2m. |
| Minimum cash / revolver limit / rate: 500 / 2,000 / 5% | judgment | Cadence opened with $3.0bn cash. These are conservative model safeguards, not disclosed company guidance. |
| Cost of equity / terminal growth: 10% / 3% | judgment | Classroom valuation assumptions: the terminal growth rate remains below the discount rate. |
| Shares outstanding: 273.312m | fact | FY2025 diluted weighted-average shares, 2025 10-K Income Statements, p. 59. |
### I — Cadence through the engine
The assumptions above replace the ABG case assumptions. The simplified FY2025 opening balance sheet used by the model is:
| Opening line | FY2025 |
|---|---:|
| Revenue | 5,296.759 |
| Inventory | 303.545 |
| PP&E, net | 517.004 |
| Other assets | 6,331.282 |
| Cash | 3,001.317 |
| Deferred revenue | 934.432 |
| Term debt | 2,480.150 |
| Revolver | 0.000 |
| Other liabilities | 1,264.385 |
| Stockholders' equity | 5,474.181 |
Running `python3 CDNS_proforma.py` produces five projected income statements, balance sheets, and cash-flow statements for FY2026–FY2030. The model estimates an equity value of $21,155.2 million, of which 74.3% comes from value after FY2030, and a value per share of **$77.40** using 273.312 million shares.
### V — Check block and market price
| Check | FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |
|---|---:|---:|---:|---:|---:|
| Assets − liabilities − equity | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Ending cash | 3,254.0 | 3,675.9 | 4,260.0 | 4,988.6 | 5,809.1 |
| Cash at or above $500 floor | Yes | Yes | Yes | Yes | Yes |
| Revolver balance | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
No forecast year draws the revolver because projected FCFE, even after the $900 million annual repurchase, keeps cash above the $500 million floor.
**Model-versus-market question:** Using the same 273.312 million-share count, the model says **$77.40 per share** and the market says **$309.09 per share at the September 23, 2026 close** (the latest completed close available on September 24); which growth, margin, capital-allocation, or discount-rate assumptions explain the difference?
At that shared share count, the market price implies equity value of approximately $84,478.0 million, compared with the model's $21,155.2 million. Price source: [Investing.com CDNS historical data](https://www.investing.com/equities/cadence-design-system-inc-historical-data), accessed September 24, 2026.
### E — Partner attack and answer
**Attack:** Why should deferred revenue remain a fixed percentage of revenue when contracts, billings, and acquisition mix can change?
**Answer:** It should not be treated as a permanent law; it is a first-pass working-capital proxy grounded in FY2025's 17.64%. I would change it if management's billings, backlog, contract-duration, or acquisition disclosures point to a sustained shift in the timing of invoicing versus revenue recognition.
### Sources
- [Cadence 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/813672/000081367226000016/cdns-20251231.htm)
- [Cadence 2024 Form 10-K](https://www.sec.gov/Archives/edgar/data/813672/000081367225000024/cdns-20241231.htm)
- [Cadence 2023 Form 10-K](https://www.sec.gov/Archives/edgar/data/813672/000081367224000034/cdns-20231231.htm)



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

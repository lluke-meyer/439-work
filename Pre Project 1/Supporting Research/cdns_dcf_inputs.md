# Cadence Design Systems DCF input record

As-of date for filing inputs: December 31, 2025. Company: Cadence Design Systems, Inc. (CDNS).

| Input | Value | Unit | Source / locator | Status |
|---    |---    |---   |---               |---     |
| Starting FCFF | 1,668.470 | USD millions | 2025 Form 10-K, Consolidated Statements of Cash Flows: operating cash flow 1,728.781 + cash interest 111.951 after tax − PP&E purchases 141.871 | sourced calculation |
| Growth, Year 1 | 14.0% | decimal | 2025 Form 10-K revenue history supports recent growth; forward forecast assumption | analyst assumption |
| Growth, Year 2 | 12.0% | decimal | 2025 Form 10-K revenue history supports recent growth; forward forecast assumption | analyst assumption |
| Growth, Year 3 | 10.0% | decimal | Forward forecast assumption | analyst assumption |
| Growth, Year 4 | 8.0% | decimal | Forward forecast assumption | analyst assumption |
| Growth, Year 5 | 5.0% | decimal | Forward forecast assumption | analyst assumption |
| WACC | 10.0% | decimal | No WACC estimate selected yet | **placeholder** |
| Terminal growth | 3.0% | decimal | Long-run economy assumption; must remain below WACC | analyst assumption |
| Non-operating cash | 3,001.317 | USD millions | 2025 Form 10-K, Consolidated Balance Sheets, cash and cash equivalents | sourced |
| Debt | 2,480.150 | USD millions | 2025 Form 10-K, Consolidated Balance Sheets, long-term debt | sourced |
| Diluted shares | 273.312 | millions of shares | 2025 Form 10-K, Consolidated Income Statements, weighted-average diluted shares | sourced |
| CDNS price | $284.60 | USD/share | Investing.com historical/current quote, accessed September 10, 2026; previous close September 9, 2026 | sourced |

## Notes

- The model follows the Lesson 6 convention: five explicit annual, end-of-year FCFF forecasts; a Gordon-growth terminal value at the end of Year 5; and discounting of the terminal value for five years.
- The tax rate used in the starting-FCFF calculation is the 2025 provision for income taxes divided by income before tax: 413.155 / 1,522.043 = 27.14%.
- The filing does not provide forward growth rates, WACC, or terminal growth. Those values are therefore assumptions, not extracted company facts.
- The WACC remains marked `placeholder` in the research record and in `dcf.py` until a sourced estimate is selected.

## Sources

- [Cadence Design Systems 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/813672/000081367226000016/cdns-20251231.htm)
- [CDNS price history and quote](https://www.investing.com/equities/cadence-design-system-inc-historical-data)

---
name: warren-buffett-expert
description: Analyze a public company as a business-quality Buffett case using five years of SEC EDGAR 10-K facts; use for owner earnings, ROE, durable economics, and an own/watch/pass memo without price data.
---

# Warren Buffett business-quality analysis

Use this skill when the user wants a repeatable Buffett-style analysis of a public company. Do not
install FAskills or use paid FAskills data sources. The bundled script is the source of every
number in the analysis; the model supplies the business judgment.

## Workflow

1. Run `scripts/sec_buffett_financials.py TICKER` from this skill folder.
2. Use only the script's printed five-year table, XBRL tags, and checks when writing the memo.
3. Judge the business as **own the business**, **watch it**, or **pass**. This week's memo does not
   use price data or estimate missing values.
4. If a fact is missing, preserve `not found`; if a required check lacks an input, preserve
   `not known` and explain that the business cannot be judged on that check.

## Data rules

- Source: SEC EDGAR company ticker and companyfacts endpoints, with a User-Agent naming the analyst
  and email. No API key is required.
- Use only filings with `form == "10-K"`, and keep the last five fiscal years labelled by fiscal
  year-end date.
- For flows, use one-year periods. When the same period appears in multiple 10-K filings, keep the
  latest filing.
- Revenue: `RevenueFromContractWithCustomerExcludingAssessedTax`, then `Revenues`.
- Net income: `NetIncomeLoss`.
- Operating cash flow: `NetCashProvidedByUsedInOperatingActivities`.
- Capital spending: `PaymentsToAcquirePropertyPlantAndEquipment`, then
  `PaymentsToAcquireProductiveAssets`.
- Equity: `StockholdersEquity`.
- ROE is net income divided by year-end equity. Owner earnings are operating cash flow minus
  capital spending.
- The three checks are: ROE of at least 15% every year; owner earnings positive every year; and
  owner earnings higher in the last year than the first year.

The Streamlit app in the parent Lab 18 folder uses this script and repeats the same missing-data
rules. Its displayed memo must contain only numbers printed by the script, and it flags any number
that is not present in that printed report.

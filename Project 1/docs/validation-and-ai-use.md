# Validation and AI Use

## Run identity

- Decision: Watch/defer; do not buy CDNS at the September 1, 2026 market price.
- Intended user: A buy-side investment committee with no current CDNS position.
- Locked-prediction commit: `8ea1229bf850b12957848c35b27fa981f74808e1`.
- Frozen repository commits: valuation package `a5ca463`; final transcripts and recording metadata `4e0d5eb`.
- Run: October 18, 2026; rerun after the decision-engine, market-expectations, industry-regime, and acquisition-overlay update.
- Valuation date: September 1, 2026.
- Source cutoff: FY2025 10-K operating-model inputs; Q2 2026 acquisition facts; latest public WACC and peer inputs available by September 1, 2026; September 1, 2026 market prices. The Hexagon layer remains separate from the integrated DCF.
- Environment: macOS 15.8.1, x86_64, Python 3.13.5, and the repository virtual environment.

## Material data and conventions

- **FY2025 opening financials**
  - Source: [Cadence FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/813672/000081367226000016/cdns-20251231.htm), December 31, 2025.
  - Treatment: Filing values divided by 1,000 and reported in USD millions.
  - Risk: The Hexagon acquisition and later 2026 balance sheet are not integrated.

- **Revenue growth, margin, and expenses**
  - Source: FY2023-FY2025 history in `Lab10 CDNS_proforma_assumptions.md`.
  - Treatment: Growth fades from 14% to 5%; margin is 86.5%; expenses fall from 67% to 65% of gross profit.
  - Risk: These are analyst assumptions, not guidance.

- **Inventory days**
  - Source: FY2025 10-K and `Lab10 CDNS_proforma_assumptions.md`.
  - Treatment: Ending inventory divided by annual cost of revenue times 365; 153.5 days.
  - Risk: Ending inventory is used instead of average inventory.

- **Deferred revenue**
  - Source: FY2025 10-K, December 31, 2025.
  - Treatment: $934.432 million, held at 17.64% of revenue.
  - Risk: Contract timing and acquisition mix can change the ratio.

- **Capex, depreciation, and tax**
  - Source: FY2025 10-K.
  - Treatment: $142 million capex; 21.5% depreciation on opening PP&E; 27% tax.
  - Risk: These are simplified forecast conventions.

- **WACC and terminal growth**
  - Source: U.S. Treasury, Damodaran's 2025 implied ERP and January 2026 industry-beta data, and Cadence's Q2 2026 Form 10-Q; calculation preserved in `docs/wacc-and-ev.md`.
  - Treatment: 10% base WACC and 3% terminal growth. Named cases use 11% downside, 10% base, and 9% upside WACC.
  - Risk: The beta is an industry estimate, and the debt cost is a recent effective-cost proxy.

- **Synopsys EV/TTM revenue**
  - Source: Synopsys FY2025 Form 10-K, Q3 2026 Form 10-Q, and September 1, 2026 closing price.
  - Treatment: 9.1249x applied to CDNS TTM revenue, then bridged with June 30, 2026 CDNS cash, debt, and shares; implied value is $189.64 per share.
  - Risk: Synopsys is one qualified peer and includes Ansys acquisition effects. This cross-check uses later bridge inputs than the integrated DCF.

- **Diluted shares**
  - Source: FY2025 10-K.
  - Treatment: 273.312 million weighted-average diluted shares.
  - Risk: This is not a September 1, 2026 spot diluted count.

- **Market price**
  - Source: [ChartExchange CDNS history](https://chartexchange.com/symbol/nasdaq-cdns/historical/), September 1, 2026.
  - Treatment: $313.04 closing price per share.
  - Risk: A one-day market price is not intrinsic value evidence.

- **Market-implied expectations dashboard**
  - Source: The accounting-linked base model and September 1, 2026 market price.
  - Treatment: Solve one input at a time for price, then test a predeclared bounded challenge. The dashboard also reports the annual growth shift required at 8%-12% WACC.
  - Result: Price requires a +32.215-point annual growth shift or 4.871% WACC with base operations. Gross margin alone has no solution below 99%. The bounded challenge reaches $203.95, or $109.09 below market.
  - Risk: Reverse DCF results identify what price implies; they do not prove the assumptions are impossible.

- **Semiconductor industry regimes**
  - Source: Base forecast plus the sourced WACC components and analyst stress assumptions.
  - Treatment: Growth, gross margin, operating leverage, beta, and WACC move together. AI buildout uses a 1.35 beta; normalization uses 1.2751; reversal uses 1.50.
  - Result: Values are $93.48, $83.20, and $54.69, respectively. The reversal moves the committee action to do not initiate.
  - Risk: Regime inputs are structured analyst stresses, not probability-weighted forecasts.

- **Hexagon D&E acquisition overlay**
  - Source: Cadence Q2 2026 Form 10-Q and February 23, 2026 Form 8-K.
  - Filing facts: $3.101 billion consideration; $2.2 billion cash; 3.224 million issued shares; $154.6 million cash acquired; $2.147 billion goodwill; $1.248 billion acquired intangibles with a 7.8-year weighted life.
  - Revenue starting point: $440 million, a rounded annualization of the $63.595 million difference between H1 2026 pro forma revenue and reported revenue for the pre-close period. Cadence states that the unaudited pro forma information is not predictive.
  - Analyst assumptions: 12%-to-4% acquired-revenue growth; 14%-to-24% EBITA margin; 0%-to-3% synergy margin; declining integration costs; 3% capex; 5% working capital on incremental revenue; 10.5% WACC; 3% terminal growth.
  - Result: $1.095 billion acquired-operation enterprise value; negative $1.852 billion value versus $2.946 billion net consideration after acquired cash; $78.93 combined illustrative value per share, or $4.41 below the standalone base.
  - Risk: This is a separate transaction-economics overlay, not a full post-acquisition statement rebuild or management forecast.

- **Committee decision rule**
  - Treatment: Initiate when intrinsic value is at least 15% above market; watch/defer when it does not clear that rule but remains above the independently modeled $57.20 downside value; do not initiate at or below that floor; stop/escalate if an integrity check fails.
  - Risk: The 15% hurdle is a disclosed committee-policy judgment. The lower boundary depends on the downside model's assumptions.

## Economic interpretation

- Derived demand: Cadence states that weaker economic conditions can reduce customers' chip designs and R&D spending, which can reduce demand for its products.
- Revenue resilience: 80% of FY2025 revenue was recurring, but recurring revenue still depends on renewals, customer investment, and product mix.
- Cost structure: R&D was 33% of FY2025 revenue. This supports testing slower revenue with costs that do not fall immediately.
- Long-duration risk: 74.1% of base enterprise value comes from terminal value. Raising WACC from 10% to 11% lowered value per share by 12.5% without changing the operating forecast.
- Cycle interaction: Stronger AI demand can increase cash-flow expectations and equity-market sensitivity at the same time. The boom regime therefore does not assume that better growth automatically lowers WACC.
- Acquisition discipline: Strategic fit is not the same as value creation. The overlay compares the acquired cash-flow value with the consideration and dilution while preserving the original DCF boundary.

This keeps the original DCF and comparable-company methods. The economic framing is that CDNS may be operationally resilient but valuation-fragile.

## Validation results

- **PASS - Official DCF training case**
  - Test: Match all seven course checkpoints within tolerance.
  - Result: All seven matched, including $27.497370 per share and 72.4014% terminal value.
  - Evidence: `outputs/validation-evidence.txt`.

- **PASS with qualifications - Source and definition**
  - Test: Recalculate one load-bearing input from the filing.
  - Result: $303.545 million inventory / $722.249 million cost of revenue x 365 = 153.40 days; the model uses 153.5.
  - Qualification: The difference is rounding, and the model uses ending rather than average inventory.
  - Evidence: FY2025 10-K and `Lab10 CDNS_proforma_assumptions.md`.

- **PASS - Base-year reconciliation**
  - Test: Opening financials match the FY2025 filing.
  - Result: Revenue, cash, inventory, PP&E, deferred revenue, debt, and equity matched.
  - Evidence: FY2025 10-K and `outputs/validation-evidence.txt`.

- **PASS - Statement articulation**
  - Test: Balance sheet and cash flow gaps equal zero each year.
  - Result: Maximum gap was $0.000000 for both checks.
  - Evidence: `tests/test_model.py` and `outputs/validation-evidence.txt`.

- **PASS - DCF direction and rate regime**
  - Test: Higher WACC lowers value; higher terminal growth raises value.
  - Result: 11% WACC lowered value from $83.34 to $72.90, or 12.5%; 3.5% growth raised it to $88.30.
  - Interpretation: This supports the valuation-fragile framing.
  - Evidence: `tests/test_model.py`.

- **PASS - Enterprise-to-equity bridge**
  - Test: EV plus cash less debt equals equity value.
  - Result: $22,256.7 + $3,001.3 - $2,480.2 = $22,777.9 million, or $83.34 per share.
  - Evidence: `outputs/visible-output.txt`.

- **PASS - Highest-risk failure**
  - Test: Stop when terminal growth equals WACC.
  - Result: The model stopped with the expected error.
  - Evidence: `tests/test_model.py` and `tests/test_app.py`.

- **PASS - Scenario stress**
  - Test: Downside value is below base and base is below upside.
  - Result: $57.20 < $83.34 < $111.52.
  - Evidence: `outputs/visible-output.txt`.

- **PASS - Result-based committee engine**
  - Test: Apply one set of disclosed thresholds to calculated outputs rather than scenario labels.
  - Result: Base and upside remain watch/defer; downside and a custom high-WACC/low-growth case return do not initiate; an artificial value above the 15% threshold returns initiate.
  - Evidence: `tests/test_model.py` and `tests/test_app.py`.

- **PASS - Market-price reconciliation**
  - Test: Feed the solved +32.215-point growth shift back through the model and compare the result with $313.04; verify that required growth rises with WACC.
  - Result: Recalculated value matches the market price within test tolerance, and the 8%-12% feasibility sequence is monotonic.
  - Evidence: `tests/test_model.py` and `outputs/visible-output.txt`.

- **PASS - Correlated industry regimes**
  - Test: Confirm reversal value is below normalization, normalization is below the extended-buildout case, and the buildout WACC remains above the 10% base because beta rises.
  - Result: $54.69 < $83.20 < $93.48; the buildout WACC is 10.319%.
  - Evidence: `tests/test_model.py` and `outputs/visible-output.txt`.

- **PASS with qualification - Acquisition overlay**
  - Test: Keep the base model unchanged, verify that higher acquired EBITA margins raise acquired enterprise value, verify the combined per-share bridge, and fail when acquisition terminal growth reaches acquisition WACC.
  - Result: All overlay tests pass. The default case produces $1.095 billion acquired EV and $78.93 combined illustrative value per share.
  - Qualification: The filing facts are sourced; operating cash-flow assumptions remain analyst judgments and are adjustable in the app.
  - Evidence: `tests/test_model.py`, `app.py`, and `outputs/visible-output.txt`.

- **PASS with qualification - Peer policy and definitions**
  - Test: Apply the written peer policy and use one consistent equity multiple and one enterprise-value multiple.
  - Result: The policy admits Synopsys and excludes Siemens EDA. Synopsys P/E implies $209.47 per share. Synopsys EV/TTM revenue is 9.1249x and implies $189.64 per CDNS share.
  - Qualification: Synopsys includes Ansys and remains the only admitted peer. The EV bridge uses the latest pre-valuation-date 2026 inputs while the DCF retains FY2025 opening balances.
  - Evidence: `Lab08 CDNS_PE_Comps.py`, `docs/wacc-and-ev.md`, and `outputs/visible-output.txt`.

- **PASS after correction - Cold run**
  - Test: Run a fresh temporary copy of the current working tree in a new virtual environment using the README commands.
  - Result: The earlier locked-version run failed under system Python because Streamlit was missing. The final October 18 run used the declared environment, regenerated visible output, and passed all 16 tests.
  - Evidence: `outputs/validation-evidence.txt`.

- **PASS with prediction mismatch - Locked changed input**
  - Test: Preserve the prediction, change only inventory days, and restore base.
  - Result: Completed below under the committed 9% WACC version; that result is preserved and was not rerun after changing the final base WACC.
  - Evidence: `outputs/validation-evidence.txt`.

## Locked changed-input record

### Precommit - complete before the run and before AI assistance on the prediction

| Timestamp | Repository commit | Material input | Old value and units | New value and units | Expected output direction | Expected decision effect |
|---|---|---|---|---|---|---|
| 3:54 PM EDT on 10/17/2026 | 475ce09d4aa361ffb3dacb5691faea97375df9e9 | Inventory Days | 153.5 days | 148.5 days | Decrease | My recommendation will remain to initiate. |

### Preserved execution result - complete only after the committed prediction

| Before output | After output | Actual decision effect | Prediction reconciliation | Failure diagnosis or reason the action did not change | Evidence path |
|---|---|---|---|---|---|
| $97.2778 per share at 153.5 days | $97.3579 per share at 148.5 days; +$0.0801 or +0.0823% | No change. The model remained watch/defer at a $313.04 market price. | Value increased, so the predicted decrease was not supported if the intended output was value per share. Inventory itself did decrease. | Lower inventory days reduced working-capital investment and increased FCFF, but the $0.08 change was too small to change the action. The predicted initiate action also conflicts with the final model's watch/defer action. | `outputs/validation-evidence.txt`; prediction locked in commit `8ea1229bf850b12957848c35b27fa981f74808e1` |

This locked record belongs to the committed 9% WACC model that existed when the prediction was made. Preserving it is more important than restating it with the later 10% WACC.

## Named AI-use register

- **OpenAI Codex; GPT-5.6 Sol - September 24-October 17, 2026**
  - Task: Pro-forma, DCF, application, tests, and documentation.
  - Output considered: AI-assisted code and valuation calculations.
  - Independent check: Official DCF case, SEC filing values, eight tests, and visible output.
  - Disposition: Accepted after testing; source and peer gaps remain qualified.
  - Decision effect: Supported the analysis but did not make the recommendation.

- **OpenAI Codex; GPT-5.6 Sol - October 17, 2026**
  - Task: Economic framing.
  - Output considered: CDNS may be operationally resilient but valuation-fragile.
  - Independent check: Recurring revenue, R&D intensity, customer-demand disclosures, terminal-value share, and the WACC test.
  - Disposition: Qualified and accepted as interpretation, not a new valuation method.
  - Decision effect: No action change; it strengthens the reason for watch/defer.

- **OpenAI Codex; GPT-5.6 Sol - October 17, 2026**
  - Task: WACC sourcing, Synopsys EV/TTM-revenue calculation, model update, and document reconciliation.
  - Output considered: 10.0% WACC and $189.64 EV/revenue reference value.
  - Independent check: U.S. Treasury data, Damodaran datasets, SEC filings, dated market prices, formula recalculation, and repository tests.
  - Disposition: Accepted with the industry-beta, effective-debt-cost, single-peer, and bridge-date qualifications stated above.
  - Decision effect: Lowered the DCF range and completed the EV cross-check; watch/defer did not change.

- **OpenAI Codex; GPT-5.6 Sol - October 18, 2026**
  - Task: Result-based decision engine, market-implied dashboard, semiconductor-cycle regimes, Hexagon acquisition overlay, expanded tests, and document reconciliation.
  - Output considered: 4.871% implied WACC, $203.95 bounded challenge, $93.48/$83.20/$54.69 regime values, and $1.095 billion acquired-operation EV with a $78.93 combined per-share illustration.
  - Independent check: Cadence Q2 2026 Form 10-Q and February 23 Form 8-K; formula review; reverse-solution rerun; monotonicity, boundary, UI, and bridge tests; PDF text and page-render checks.
  - Disposition: Accepted with explicit separation between filing facts, policy thresholds, industry stresses, acquisition assumptions, and the unchanged accounting-linked base model.
  - Decision effect: Watch/defer did not change. The update makes the burden of proof and the conditions for changing the action more explicit.

## Limitations, monitoring, and kill or escalation rules

- Limitations: The model uses FY2025 opening balances, simplified other assets and liabilities, and one qualified peer. The Hexagon overlay is not a full post-acquisition statement rebuild, does not claim probability weights, and depends on analyst assumptions for acquired revenue, margin, synergies, integration costs, reinvestment, and WACC. The EV cross-check continues to use a separately disclosed June 2026 bridge rather than silently changing the DCF opening balances.
- Monitoring: Review semiconductor design activity, customer R&D spending, recurring revenue, RPO, Cadence R&D intensity, margins, cash, debt, shares, and WACC after each quarterly filing.
- Reversal trigger: Initiate only if updated acquisition-aware cash flows and peer evidence support a value range near or above the market price with a margin of safety. Move to do not initiate if weaker growth, margins, or leverage make the downside case more likely.
- Kill or escalate: Stop if a source is stale, the statements do not tie, terminal growth reaches WACC, an acquisition bridge is incomplete, or a method mixes the FY2025 DCF, Hexagon overlay, or 2026 peer bridge without disclosure.

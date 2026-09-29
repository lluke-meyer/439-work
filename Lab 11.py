##### Lab 11 #####


### D

# CDNS's forecast is driven mainly by revenue growth, gross margin, op. expenses as a percentage of gross profit, capital spending and depreciation, deferred revenue, and taxes because they determine op. income and FCFE, while cost of equity and terminal growth determine how those cash flows translate into VPS.


### R

# 1. I chose to use CDNS's revenue growth and their op. expenses as a percentage of gross profit.
# 2.
    # Revenue-growth path
        # Base values: FY2026 14.0%, FY2027 12.0%, FY2028 10.0%, FY2029 8.0%, FY2030 5.0%
        # Lower values: FY2026 12.0%, FY2027 10.0%, FY2028 8.0%, FY2029 6.0%, FY2030 3.0%
        # Higher values: FY2026 16.0%, FY2027 14.0%, FY2028 12.0%, FY2029 10.0%, FY2030 7.0%
        # Units and affected years: annual revenue growth rates in percentage points, FY2026-FY2030
        # Base rationale: FY2025 revenue growth was 14.1%; the base path fades as CDNS matures.
        # Range rationale: I used a two-point range because revenue growth should fade as CDNS matures, but the lower and higher paths still keep the same pattern as my base case.
    # Operating expenses as a percentage of gross profit
        # Base values: FY2026 67.0%, FY2027 66.5%, FY2028 66.0%, FY2029 65.5%, FY2030 65.0%
        # Lower values: FY2026 66.5%, FY2027 66.0%, FY2028 65.5%, FY2029 65.0%, FY2030 64.5%
        # Higher values: FY2026 67.5%, FY2027 67.0%, FY2028 66.5%, FY2029 66.0%, FY2030 65.5%
        # Units and affected years: operating expenses divided by gross profit in percentage points, FY2026-FY2030
        # Base rationale: FY2025 was 67.4%; the base path assumes CDNS slowly reins in costs as it matures.
        # Range rationale: I used a narrower half-point range because I do not expect this ratio to change much.
# 3. Comparable outputs for every run: FY2030 operating profit (USD millions), FY2030 FCFE (USD millions), and value per share (USD per share).


### I

# I kept my Lab 10 model intact and added a sensitivity analysis below.

from copy import deepcopy
from math import isclose

YEARS = tuple(range(2026, 2031))

BASE_INPUTS = {
    "revenue_growth": [0.14, 0.12, 0.10, 0.08, 0.05],
    "gross_margin": 0.865,
    "opex_to_gross_profit": [0.670, 0.665, 0.660, 0.655, 0.650],
    "depreciation_rate": 111.4 / 517.004,
    "capex": 142.0,
    "tax_rate": 0.27,
    "inventory_days": 153.5,
    "deferred_revenue_ratio": 934.432 / 5_296.759,
    "minimum_cash": 500.0,
    "revolver_limit": 2_000.0,
    "revolver_rate": 0.05,
    "debt_repayment": 0.0,
    "share_buyback": 900.0,
    "term_debt_rate": 116.541 / 2_476.183,
    "cost_of_equity": 0.10,
    "terminal_growth": 0.03,
    "shares_outstanding": 273.312,
    "opening": {
        "revenue": 5_296.759,
        "inventory": 303.545,
        "ppe": 517.004,
        "other_assets": 6_331.282,
        "cash": 3_001.317,
        "deferred_revenue": 934.432,
        "debt": 2_480.150,
        "revolver": 0.0,
        "other_liabilities": 1_264.385,
        "equity": 5_474.181,
    },
}

SENSITIVITY_DRIVERS = (
    {
        "name": "Revenue-growth path",
        "key": "revenue_growth",
        "unit": "annual revenue growth",
        "cases": {
            "Lower": [0.12, 0.10, 0.08, 0.06, 0.03],
            "Base": [0.14, 0.12, 0.10, 0.08, 0.05],
            "Higher": [0.16, 0.14, 0.12, 0.10, 0.07],
        },
    },
    {
        "name": "Operating expenses / gross profit",
        "key": "opex_to_gross_profit",
        "unit": "operating expenses as a percentage of gross profit",
        "cases": {
            "Lower": [0.665, 0.660, 0.655, 0.650, 0.645],
            "Base": [0.670, 0.665, 0.660, 0.655, 0.650],
            "Higher": [0.675, 0.670, 0.665, 0.660, 0.655],
        },
    },
)


def balance_gap(forecast):
    assets = forecast["inventory"] + forecast["ppe"] + forecast["other_assets"] + forecast["cash"]
    claims = (forecast["deferred_revenue"] + forecast["debt"] + forecast["revolver"]
              + forecast["other_liabilities"] + forecast["equity"])
    return assets - claims


def assert_balanced(year, forecast, inputs):
    gap = balance_gap(forecast)
    if abs(gap) > 1e-6:
        raise ValueError(f"FY{year}E is not balanced: gap of {gap:.1f}")
    if forecast["cash"] < inputs["minimum_cash"] - 1e-6:
        difference = forecast["cash"] - inputs["minimum_cash"]
        raise ValueError(f"FY{year}E cash is below the minimum: {difference:.1f}")


def build_forecast(inputs):
    forecasts = []
    opening = deepcopy(inputs["opening"])
    for year, growth, opex_ratio in zip(
            YEARS, inputs["revenue_growth"], inputs["opex_to_gross_profit"]):
        forecast = {"revenue": opening["revenue"] * (1 + growth)}
        forecast["gross_profit"] = forecast["revenue"] * inputs["gross_margin"]
        forecast["opex"] = forecast["gross_profit"] * opex_ratio
        forecast["depreciation"] = opening["ppe"] * inputs["depreciation_rate"]
        forecast["operating_income"] = (
            forecast["gross_profit"] - forecast["opex"] - forecast["depreciation"]
        )
        forecast["interest"] = (
            opening["debt"] * inputs["term_debt_rate"]
            + opening["revolver"] * inputs["revolver_rate"]
        )
        forecast["pretax_income"] = forecast["operating_income"] - forecast["interest"]
        forecast["tax"] = max(0.0, forecast["pretax_income"]) * inputs["tax_rate"]
        forecast["net_income"] = forecast["pretax_income"] - forecast["tax"]

        cogs = forecast["revenue"] - forecast["gross_profit"]
        forecast["inventory"] = cogs * inputs["inventory_days"] / 365
        forecast["deferred_revenue"] = forecast["revenue"] * inputs["deferred_revenue_ratio"]
        forecast["ppe"] = opening["ppe"] + inputs["capex"] - forecast["depreciation"]
        forecast["other_assets"] = opening["other_assets"]
        forecast["other_liabilities"] = opening["other_liabilities"]
        forecast["debt"] = opening["debt"] - inputs["debt_repayment"]
        forecast["equity"] = opening["equity"] + forecast["net_income"] - inputs["share_buyback"]

        forecast["inventory_change"] = forecast["inventory"] - opening["inventory"]
        forecast["deferred_revenue_change"] = (
            forecast["deferred_revenue"] - opening["deferred_revenue"]
        )
        forecast["fcfe"] = (
            forecast["net_income"]
            + forecast["depreciation"]
            - inputs["capex"]
            - forecast["inventory_change"]
            + forecast["deferred_revenue_change"]
            - inputs["debt_repayment"]
        )
        cash_before_revolver = opening["cash"] + forecast["fcfe"] - inputs["share_buyback"]
        revolver_change = 0.0
        if cash_before_revolver < inputs["minimum_cash"]:
            revolver_change = inputs["minimum_cash"] - cash_before_revolver
            if opening["revolver"] + revolver_change > inputs["revolver_limit"]:
                raise ValueError(f"FY{year}E revolver limit exceeded")
        elif opening["revolver"]:
            revolver_change = -min(
                opening["revolver"], cash_before_revolver - inputs["minimum_cash"]
            )
        forecast["revolver"] = opening["revolver"] + revolver_change
        forecast["cash"] = cash_before_revolver + revolver_change
        forecast["revolver_change"] = revolver_change
        assert_balanced(year, forecast, inputs)
        forecasts.append(forecast)
        opening = forecast
    return forecasts


def value_equity(forecasts, inputs):
    if inputs["cost_of_equity"] <= inputs["terminal_growth"]:
        raise ValueError("Cost of equity must be greater than terminal growth")
    if inputs["shares_outstanding"] <= 0:
        raise ValueError("Shares outstanding must be positive")
    pv_fcfe = sum(
        forecast["fcfe"] / (1 + inputs["cost_of_equity"]) ** period
        for period, forecast in enumerate(forecasts, 1)
    )
    terminal_fcfe = forecasts[-1]["fcfe"] + inputs["debt_repayment"]
    terminal_value = (
        terminal_fcfe * (1 + inputs["terminal_growth"])
        / (inputs["cost_of_equity"] - inputs["terminal_growth"])
    )
    pv_terminal = terminal_value / (1 + inputs["cost_of_equity"]) ** len(forecasts)
    equity_value = pv_fcfe + pv_terminal
    return equity_value, pv_terminal / equity_value, equity_value / inputs["shares_outstanding"]


def run_model(inputs):
    try:
        forecasts = build_forecast(inputs)
    except ValueError as error:
        return {"valid": False, "error": str(error), "inputs": inputs}

    max_gap = max(abs(balance_gap(forecast)) for forecast in forecasts)
    cash_check = all(forecast["cash"] >= inputs["minimum_cash"] - 1e-6 for forecast in forecasts)
    result = {
        "valid": True,
        "error": "",
        "inputs": inputs,
        "forecasts": forecasts,
        "operating_profit": forecasts[-1]["operating_income"],
        "fcfe": forecasts[-1]["fcfe"],
        "max_gap": max_gap,
        "cash_check": cash_check,
    }
    try:
        equity_value, terminal_share, value_per_share = value_equity(forecasts, inputs)
        result.update({
            "equity_value": equity_value,
            "terminal_share": terminal_share,
            "value_per_share": value_per_share,
            "valuation_note": "",
        })
    except ValueError as error:
        result.update({
            "equity_value": None,
            "terminal_share": None,
            "value_per_share": None,
            "valuation_note": str(error),
        })
    return result


def show(title, rows, forecasts):
    print(f"\n{title}\n{'USD millions':<30}" + "".join(f"FY{year}E{'':>8}" for year in YEARS))
    for label, key in rows:
        print(f"{label:<30}" + "".join(f"{forecast[key]:>13.1f}" for forecast in forecasts))


def show_base_model(result):
    forecasts = result["forecasts"]
    inputs = result["inputs"]
    print("\nInitial Base Run")
    show("Income Statement", [
        ("Revenue", "revenue"),
        ("Gross profit", "gross_profit"),
        ("Operating expenses", "opex"),
        ("PP&E depreciation", "depreciation"),
        ("Operating income", "operating_income"),
        ("Interest", "interest"),
        ("Tax", "tax"),
        ("Net income", "net_income"),
    ], forecasts)
    show("Balance Sheet", [
        ("Inventory", "inventory"),
        ("PP&E", "ppe"),
        ("Other assets", "other_assets"),
        ("Cash", "cash"),
        ("Deferred revenue", "deferred_revenue"),
        ("Term debt", "debt"),
        ("Revolver", "revolver"),
        ("Other liabilities", "other_liabilities"),
        ("Equity", "equity"),
    ], forecasts)
    cash_flow_forecasts = [
        dict(forecast, capex=inputs["capex"], buyback=inputs["share_buyback"])
        for forecast in forecasts
    ]
    show("Cash Flow", [
        ("Net income", "net_income"),
        ("Depreciation", "depreciation"),
        ("Capital spending", "capex"),
        ("Change in inventory", "inventory_change"),
        ("Change in deferred revenue", "deferred_revenue_change"),
        ("Free cash flow to equity", "fcfe"),
        ("Share buyback", "buyback"),
        ("Change in revolver", "revolver_change"),
        ("Ending cash", "cash"),
    ], cash_flow_forecasts)
    print("\nChecks")
    for year, forecast in zip(YEARS, forecasts):
        print(
            f"FY{year}E  Assets - liabilities - equity: {balance_gap(forecast):.1f}  "
            f"Cash >= minimum: {forecast['cash'] >= inputs['minimum_cash']}"
        )
    print(
        f"\nValuation\nEquity value: ${result['equity_value']:,.1f} million"
        f"\nShare of value after 2030: {result['terminal_share']:.1%}"
        f"\nValue per share: ${result['value_per_share']:,.2f}"
    )


def run_sensitivity():
    results = []
    for driver in SENSITIVITY_DRIVERS:
        for case_name, case_values in driver["cases"].items():
            case_inputs = deepcopy(BASE_INPUTS)
            case_inputs[driver["key"]] = deepcopy(case_values)
            result = run_model(case_inputs)
            result.update({
                "driver": driver["name"],
                "driver_key": driver["key"],
                "unit": driver["unit"],
                "case": case_name,
                "case_values": case_values,
            })
            results.append(result)
    return results


def format_path(values):
    return ", ".join(f"{value:.1%}" for value in values)


def show_sensitivity(results, base_result):
    print("\nOne-at-a-Time Sensitivity")
    for driver in SENSITIVITY_DRIVERS:
        driver_results = [result for result in results if result["driver"] == driver["name"]]
        print(f"\nDriver: {driver['name']}")
        print(f"Units: {driver['unit']}; values shown for FY2026-FY2030")
        print(
            f"{'Case':<8}{'Actual input values':<39}{'Op. profit':>12}{'Change':>12}"
            f"{'FCFE':>12}{'Change':>12}{'VPS':>10}{'Change':>10}{'Check':>9}"
        )
        for result in driver_results:
            if not result["valid"]:
                print(f"{result['case']:<8}{format_path(result['case_values']):<39}{'n.a.':>56}  INVALID")
                print(f"  Reason: {result['error']}")
                continue
            operating_change = result["operating_profit"] - base_result["operating_profit"]
            fcfe_change = result["fcfe"] - base_result["fcfe"]
            if result["value_per_share"] is None:
                value_text = "n.a."
                value_change_text = "n.a."
            else:
                value_text = f"{result['value_per_share']:.2f}"
                value_change_text = f"{result['value_per_share'] - base_result['value_per_share']:+.2f}"
            check = "PASS" if result["max_gap"] <= 1e-6 and result["cash_check"] else "FAIL"
            print(
                f"{result['case']:<8}{format_path(result['case_values']):<39}"
                f"{result['operating_profit']:>12.1f}{operating_change:>+12.1f}"
                f"{result['fcfe']:>12.1f}{fcfe_change:>+12.1f}"
                f"{value_text:>10}{value_change_text:>10}{check:>9}"
            )

        valid_results = [result for result in driver_results if result["valid"]]
        operating_span = max(result["operating_profit"] for result in valid_results) - min(
            result["operating_profit"] for result in valid_results
        )
        fcfe_span = max(result["fcfe"] for result in valid_results) - min(
            result["fcfe"] for result in valid_results
        )
        valid_values = [
            result["value_per_share"] for result in valid_results
            if result["value_per_share"] is not None
        ]
        value_span = max(valid_values) - min(valid_values) if valid_values else None
        value_span_text = f"${value_span:.2f}/share" if value_span is not None else "n.a."
        print(
            f"Output spans over these ranges: operating profit ${operating_span:,.1f} million; "
            f"FCFE ${fcfe_span:,.1f} million; value per share {value_span_text}."
        )


def show_final_year_trace(results):
    print("\nFY2030 Trace Details (USD millions)")
    print(
        f"{'Driver / case':<43}{'Revenue':>11}{'Gross profit':>14}{'Op. exp.':>11}"
        f"{'Deprec.':>10}{'Op. profit':>12}{'Net income':>12}{'Inv. change':>12}"
        f"{'Def. rev. change':>17}{'FCFE':>11}"
    )
    for result in results:
        if not result["valid"]:
            continue
        forecast = result["forecasts"][-1]
        label = f"{result['driver']} - {result['case']}"
        print(
            f"{label:<43}{forecast['revenue']:>11.1f}{forecast['gross_profit']:>14.1f}"
            f"{forecast['opex']:>11.1f}{forecast['depreciation']:>10.1f}"
            f"{forecast['operating_income']:>12.1f}{forecast['net_income']:>12.1f}"
            f"{forecast['inventory_change']:>12.1f}{forecast['deferred_revenue_change']:>17.1f}"
            f"{forecast['fcfe']:>11.1f}"
        )


def show_restored_base(base_before, base_after, base_snapshot):
    input_check = BASE_INPUTS == base_snapshot
    operating_difference = base_after["operating_profit"] - base_before["operating_profit"]
    fcfe_difference = base_after["fcfe"] - base_before["fcfe"]
    value_difference = base_after["value_per_share"] - base_before["value_per_share"]
    output_check = all((
        isclose(operating_difference, 0.0, abs_tol=1e-9),
        isclose(fcfe_difference, 0.0, abs_tol=1e-9),
        isclose(value_difference, 0.0, abs_tol=1e-9),
    ))
    accounting_check = (
        base_after["valid"] and base_after["max_gap"] <= 1e-6 and base_after["cash_check"]
    )
    print("\nRestored Base Check")
    print(f"Base inputs restored: {'PASS' if input_check else 'FAIL'}")
    print(f"FY2030 operating profit difference: {operating_difference:+.6f} million")
    print(f"FY2030 FCFE difference: {fcfe_difference:+.6f} million")
    print(f"Value per share difference: {value_difference:+.6f}")
    print(f"Base outputs match: {'PASS' if output_check else 'FAIL'}")
    print(f"Accounting checks: {'PASS' if accounting_check else 'FAIL'}")


def main():
    base_snapshot = deepcopy(BASE_INPUTS)
    base_before = run_model(deepcopy(BASE_INPUTS))
    if not base_before["valid"]:
        raise ValueError(f"Initial base run failed: {base_before['error']}")
    show_base_model(base_before)

    sensitivity_results = run_sensitivity()
    show_sensitivity(sensitivity_results, base_before)
    show_final_year_trace(sensitivity_results)

    base_after = run_model(deepcopy(BASE_INPUTS))
    if not base_after["valid"]:
        raise ValueError(f"Restored base run failed: {base_after['error']}")
    show_restored_base(base_before, base_after, base_snapshot)


if __name__ == "__main__":
    main()


### V

# Peyton's result passed with flying colors and all outputs match what we expected.


### E

# Over these ranges, revenue growth was the larger driver. Its spans were $465.9 million for op. profit, $385.6 million for FCFE, and $15.71 for VPS, compared with $73.0 million, $53.3 million, and $2.41 for the op. expense ratio.
# Revenue growth changes sales, which flows through gross profit, op. profit, FCFE, and terminal value. This ranking could reflect my wider revenue-growth range, so it does not prove revenue growth is always the more important driver.


### R

# One-at-a-time sensitivity changes one input while every other independent input stays at base. A wider input range can create a larger output span, and the table is not a probability because it does not assign odds or change several assumptions together.
# Revenue growth mattered most over my ranges. I was surprised that the half-point op. expense range changed VPS by only $2.41.



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

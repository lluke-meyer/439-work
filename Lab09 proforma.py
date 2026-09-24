"""Five-year ABG pro-forma model (USD millions, except per-share data)."""


YEARS = range(2026, 2031)

# Assumptions
REVENUE_GROWTH = 0.018
GROSS_MARGIN = 0.1705
SGA_RATIOS = [0.665, 0.655, 0.645, 0.645, 0.645]
DEPRECIATION_RATE = 82.4 / 3_070.4
IMPAIRMENT = 120.0
CAPEX = 250.0
TAX_RATE = 0.255
INVENTORY_DAYS = 2_135.8 / (17_999.0 - 3_071.7) * 365
FLOOR_PLAN_RATIO = 2_027.0 / 2_135.8
OTHER_WORKING_CAPITAL_RATE = 0.008
MINIMUM_CASH = 25.0
REVOLVER_LIMIT = 850.0
REVOLVER_RATE = 0.06
DEBT_REPAYMENT = 150.0
SHARE_BUYBACK = 150.0
FLOOR_PLAN_RATE = 0.0467
TERM_DEBT_RATE = 0.0544
COST_OF_EQUITY = 0.10
TERMINAL_GROWTH = 0.025
SHARES_OUTSTANDING = 17.951349

# FY2025 opening balance sheet
OPENING = {
    "revenue": 17_999.0,
    "inventory": 2_135.8,
    "ppe": 3_070.4,
    "other_assets": 6_371.6,
    "cash": 40.4,
    "floor_plan": 2_027.0,
    "debt": 3_572.0,
    "revolver": 0.0,
    "other_liabilities": 2_127.5,
    "equity": 3_891.7,
}


def print_table(title, rows, forecasts):
    """Print a compact statement with forecast years across the columns."""
    print(f"\n{title}")
    print(f"{'USD millions':<32}" + "".join(f"FY{year}E{'':>9}" for year in YEARS))
    for label, key in rows:
        print(f"{label:<32}" + "".join(f"{forecast[key]:>15.1f}" for forecast in forecasts))


def assert_balanced(year, forecast):
    """Refuse to value a forecast with an unbalanced balance sheet or low cash."""
    assets = forecast["inventory"] + forecast["ppe"] + forecast["other_assets"] + forecast["cash"]
    liabilities_and_equity = (
        forecast["floor_plan"]
        + forecast["debt"]
        + forecast["revolver"]
        + forecast["other_liabilities"]
        + forecast["equity"]
    )
    gap = assets - liabilities_and_equity
    if abs(gap) > 1e-6:
        raise ValueError(f"FY{year}E is not balanced: gap of {gap:.1f}")
    if forecast["cash"] < MINIMUM_CASH - 1e-6:
        raise ValueError(
            f"FY{year}E cash is below the minimum: "
            f"{forecast['cash'] - MINIMUM_CASH:.1f}"
        )


def build_forecast():
    forecasts = []
    opening = OPENING.copy()

    for year, sga_ratio in zip(YEARS, SGA_RATIOS):
        forecast = {}
        forecast["revenue"] = opening["revenue"] * (1 + REVENUE_GROWTH)
        forecast["gross_profit"] = forecast["revenue"] * GROSS_MARGIN
        forecast["sga"] = forecast["gross_profit"] * sga_ratio
        forecast["depreciation"] = opening["ppe"] * DEPRECIATION_RATE
        forecast["impairment"] = IMPAIRMENT
        forecast["operating_income"] = (
            forecast["gross_profit"]
            - forecast["sga"]
            - forecast["depreciation"]
            - forecast["impairment"]
        )
        forecast["interest"] = (
            opening["floor_plan"] * FLOOR_PLAN_RATE
            + opening["debt"] * TERM_DEBT_RATE
            + opening["revolver"] * REVOLVER_RATE
        )
        forecast["pretax_income"] = forecast["operating_income"] - forecast["interest"]
        forecast["tax"] = max(0.0, forecast["pretax_income"]) * TAX_RATE
        forecast["net_income"] = forecast["pretax_income"] - forecast["tax"]

        # Balance sheet, with cash calculated last.
        forecast["inventory"] = (
            (forecast["revenue"] - forecast["gross_profit"]) * INVENTORY_DAYS / 365
        )
        forecast["floor_plan"] = forecast["inventory"] * FLOOR_PLAN_RATIO
        forecast["ppe"] = opening["ppe"] + CAPEX - forecast["depreciation"]
        revenue_change = forecast["revenue"] - opening["revenue"]
        forecast["other_working_capital"] = OTHER_WORKING_CAPITAL_RATE * revenue_change
        forecast["other_assets"] = (
            opening["other_assets"]
            + forecast["other_working_capital"]
            - forecast["impairment"]
        )
        forecast["debt"] = opening["debt"] - DEBT_REPAYMENT
        forecast["other_liabilities"] = opening["other_liabilities"]
        forecast["equity"] = opening["equity"] + forecast["net_income"] - SHARE_BUYBACK

        inventory_change = forecast["inventory"] - opening["inventory"]
        floor_plan_change = forecast["floor_plan"] - opening["floor_plan"]
        forecast["inventory_change"] = inventory_change
        forecast["floor_plan_change"] = floor_plan_change
        forecast["capex"] = CAPEX
        forecast["debt_repayment"] = DEBT_REPAYMENT
        forecast["fcfe"] = (
            forecast["net_income"]
            + forecast["depreciation"]
            + forecast["impairment"]
            - CAPEX
            - inventory_change
            - forecast["other_working_capital"]
            + floor_plan_change
            - DEBT_REPAYMENT
        )

        cash_before_revolver = opening["cash"] + forecast["fcfe"] - SHARE_BUYBACK
        revolver_change = 0.0
        if cash_before_revolver < MINIMUM_CASH:
            revolver_change = MINIMUM_CASH - cash_before_revolver
            if opening["revolver"] + revolver_change > REVOLVER_LIMIT:
                raise ValueError(f"FY{year}E revolver limit exceeded")
        elif opening["revolver"] > 0:
            revolver_change = -min(opening["revolver"], cash_before_revolver - MINIMUM_CASH)
        forecast["revolver"] = opening["revolver"] + revolver_change
        forecast["cash"] = cash_before_revolver + revolver_change
        forecast["opening_cash"] = opening["cash"]
        forecast["revolver_change"] = revolver_change

        assert_balanced(year, forecast)
        forecasts.append(forecast)
        opening = forecast

    return forecasts


def value_equity(forecasts):
    present_value_fcfe = sum(
        forecast["fcfe"] / (1 + COST_OF_EQUITY) ** period
        for period, forecast in enumerate(forecasts, start=1)
    )
    terminal_fcfe = forecasts[-1]["fcfe"] + DEBT_REPAYMENT
    terminal_value = terminal_fcfe * (1 + TERMINAL_GROWTH) / (COST_OF_EQUITY - TERMINAL_GROWTH)
    present_value_terminal = terminal_value / (1 + COST_OF_EQUITY) ** len(forecasts)
    equity_value = present_value_fcfe + present_value_terminal
    return equity_value, present_value_terminal / equity_value, equity_value / SHARES_OUTSTANDING


def main():
    forecasts = build_forecast()
    print_table(
        "Income Statement",
        [
            ("Revenue", "revenue"),
            ("Gross profit", "gross_profit"),
            ("SG&A", "sga"),
            ("Depreciation", "depreciation"),
            ("Impairment", "impairment"),
            ("Operating income", "operating_income"),
            ("Interest", "interest"),
            ("Pretax income", "pretax_income"),
            ("Tax", "tax"),
            ("Net income", "net_income"),
        ],
        forecasts,
    )
    print_table(
        "Balance Sheet",
        [
            ("Inventory", "inventory"), ("PP&E", "ppe"), ("Other assets", "other_assets"),
            ("Cash", "cash"), ("Floor plan", "floor_plan"), ("Term debt", "debt"),
            ("Revolver", "revolver"), ("Other liabilities", "other_liabilities"), ("Equity", "equity"),
        ],
        forecasts,
    )
    print_table(
        "Cash Flow",
        [
            ("Net income", "net_income"), ("Depreciation", "depreciation"),
            ("Impairment", "impairment"), ("Capital spending", "capex"),
            ("Change in inventory", "inventory_change"),
            ("Change in other working capital", "other_working_capital"),
            ("Change in floor plan", "floor_plan_change"), ("Debt repayment", "debt_repayment"),
            ("Free cash flow to equity", "fcfe"), ("Share buyback", "share_buyback"),
            ("Change in revolver", "revolver_change"), ("Ending cash", "cash"),
        ],
        [dict(forecast, share_buyback=SHARE_BUYBACK) for forecast in forecasts],
    )

    print("\nChecks")
    for year, forecast in zip(YEARS, forecasts):
        assets = forecast["inventory"] + forecast["ppe"] + forecast["other_assets"] + forecast["cash"]
        liabilities_and_equity = forecast["floor_plan"] + forecast["debt"] + forecast["revolver"] + forecast["other_liabilities"] + forecast["equity"]
        print(f"FY{year}E  Assets - liabilities - equity: {assets - liabilities_and_equity:.1f}  Cash >= minimum: {forecast['cash'] >= MINIMUM_CASH}")

    equity_value, terminal_share, value_per_share = value_equity(forecasts)
    print("\nValuation")
    print(f"Equity value: ${equity_value:,.1f} million")
    print(f"Share of value after 2030: {terminal_share:.1%}")
    print(f"Value per share: ${value_per_share:,.2f}")


if __name__ == "__main__":
    main()



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

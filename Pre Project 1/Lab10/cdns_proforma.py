"""Cadence Design Systems five-year pro-forma (USD millions, except per-share data)."""

YEARS = range(2026, 2031)

# See CDNS_proforma_assumptions.md for labels, arithmetic, and filing locators.
REVENUE_GROWTH = [0.14, 0.12, 0.10, 0.08, 0.05]
GROSS_MARGIN = 0.865
OPEX_TO_GROSS_PROFIT = [0.670, 0.665, 0.660, 0.655, 0.650]
DEPRECIATION_RATE = 111.4 / 517.004
CAPEX = 142.0
TAX_RATE = 0.27
INVENTORY_DAYS = 153.5
DEFERRED_REVENUE_RATIO = 934.432 / 5_296.759
MINIMUM_CASH = 500.0
REVOLVER_LIMIT = 2_000.0
REVOLVER_RATE = 0.05
DEBT_REPAYMENT = 0.0
SHARE_BUYBACK = 900.0
TERM_DEBT_RATE = 116.541 / 2_476.183
COST_OF_EQUITY = 0.10
TERMINAL_GROWTH = 0.03
SHARES_OUTSTANDING = 273.312

# FY2025 simplified opening balance sheet. "Other" lines are held flat deliberately.
OPENING = {
    "revenue": 5_296.759, "inventory": 303.545, "ppe": 517.004,
    "other_assets": 6_331.282, "cash": 3_001.317,
    "deferred_revenue": 934.432, "debt": 2_480.150,
    "revolver": 0.0, "other_liabilities": 1_264.385, "equity": 5_474.181,
}


def assert_balanced(year, f):
    assets = f["inventory"] + f["ppe"] + f["other_assets"] + f["cash"]
    claims = f["deferred_revenue"] + f["debt"] + f["revolver"] + f["other_liabilities"] + f["equity"]
    gap = assets - claims
    if abs(gap) > 1e-6:
        raise ValueError(f"FY{year}E is not balanced: gap of {gap:.1f}")
    if f["cash"] < MINIMUM_CASH - 1e-6:
        raise ValueError(f"FY{year}E cash is below the minimum: {f['cash'] - MINIMUM_CASH:.1f}")


def build_forecast():
    forecasts, opening = [], OPENING.copy()
    for year, growth, opex_ratio in zip(YEARS, REVENUE_GROWTH, OPEX_TO_GROSS_PROFIT):
        f = {"revenue": opening["revenue"] * (1 + growth)}
        f["gross_profit"] = f["revenue"] * GROSS_MARGIN
        f["opex"] = f["gross_profit"] * opex_ratio
        f["depreciation"] = opening["ppe"] * DEPRECIATION_RATE
        f["operating_income"] = f["gross_profit"] - f["opex"] - f["depreciation"]
        f["interest"] = opening["debt"] * TERM_DEBT_RATE + opening["revolver"] * REVOLVER_RATE
        f["pretax_income"] = f["operating_income"] - f["interest"]
        f["tax"] = max(0.0, f["pretax_income"]) * TAX_RATE
        f["net_income"] = f["pretax_income"] - f["tax"]

        cogs = f["revenue"] - f["gross_profit"]
        f["inventory"] = cogs * INVENTORY_DAYS / 365
        f["deferred_revenue"] = f["revenue"] * DEFERRED_REVENUE_RATIO
        f["ppe"] = opening["ppe"] + CAPEX - f["depreciation"]
        f["other_assets"] = opening["other_assets"]
        f["other_liabilities"] = opening["other_liabilities"]
        f["debt"] = opening["debt"] - DEBT_REPAYMENT
        f["equity"] = opening["equity"] + f["net_income"] - SHARE_BUYBACK

        f["inventory_change"] = f["inventory"] - opening["inventory"]
        f["deferred_revenue_change"] = f["deferred_revenue"] - opening["deferred_revenue"]
        f["fcfe"] = (f["net_income"] + f["depreciation"] - CAPEX - f["inventory_change"]
                     + f["deferred_revenue_change"] - DEBT_REPAYMENT)
        cash_before_revolver = opening["cash"] + f["fcfe"] - SHARE_BUYBACK
        revolver_change = 0.0
        if cash_before_revolver < MINIMUM_CASH:
            revolver_change = MINIMUM_CASH - cash_before_revolver
            if opening["revolver"] + revolver_change > REVOLVER_LIMIT:
                raise ValueError(f"FY{year}E revolver limit exceeded")
        elif opening["revolver"]:
            revolver_change = -min(opening["revolver"], cash_before_revolver - MINIMUM_CASH)
        f["revolver"] = opening["revolver"] + revolver_change
        f["cash"] = cash_before_revolver + revolver_change
        f["revolver_change"] = revolver_change
        assert_balanced(year, f)
        forecasts.append(f)
        opening = f
    return forecasts


def show(title, rows, forecasts):
    print(f"\n{title}\n{'USD millions':<30}" + "".join(f"FY{y}E{'':>8}" for y in YEARS))
    for label, key in rows:
        print(f"{label:<30}" + "".join(f"{f[key]:>13.1f}" for f in forecasts))


def value_equity(forecasts):
    pv_fcfe = sum(f["fcfe"] / (1 + COST_OF_EQUITY) ** n for n, f in enumerate(forecasts, 1))
    terminal_fcfe = forecasts[-1]["fcfe"] + DEBT_REPAYMENT
    terminal_value = terminal_fcfe * (1 + TERMINAL_GROWTH) / (COST_OF_EQUITY - TERMINAL_GROWTH)
    pv_terminal = terminal_value / (1 + COST_OF_EQUITY) ** len(forecasts)
    equity_value = pv_fcfe + pv_terminal
    return equity_value, pv_terminal / equity_value, equity_value / SHARES_OUTSTANDING


def main():
    forecasts = build_forecast()
    show("Income Statement", [("Revenue", "revenue"), ("Gross profit", "gross_profit"),
         ("Operating expenses", "opex"), ("PP&E depreciation", "depreciation"),
         ("Operating income", "operating_income"), ("Interest", "interest"),
         ("Tax", "tax"), ("Net income", "net_income")], forecasts)
    show("Balance Sheet", [("Inventory", "inventory"), ("PP&E", "ppe"), ("Other assets", "other_assets"),
         ("Cash", "cash"), ("Deferred revenue", "deferred_revenue"), ("Term debt", "debt"),
         ("Revolver", "revolver"), ("Other liabilities", "other_liabilities"), ("Equity", "equity")], forecasts)
    show("Cash Flow", [("Net income", "net_income"), ("Depreciation", "depreciation"), ("Capital spending", "capex"),
         ("Change in inventory", "inventory_change"), ("Change in deferred revenue", "deferred_revenue_change"),
         ("Free cash flow to equity", "fcfe"), ("Share buyback", "buyback"),
         ("Change in revolver", "revolver_change"), ("Ending cash", "cash")],
         [dict(f, capex=CAPEX, buyback=SHARE_BUYBACK) for f in forecasts])
    print("\nChecks")
    for year, f in zip(YEARS, forecasts):
        gap = f["inventory"] + f["ppe"] + f["other_assets"] + f["cash"] - f["deferred_revenue"] - f["debt"] - f["revolver"] - f["other_liabilities"] - f["equity"]
        print(f"FY{year}E  Assets - liabilities - equity: {gap:.1f}  Cash >= minimum: {f['cash'] >= MINIMUM_CASH}")
    value, terminal_share, per_share = value_equity(forecasts)
    print(f"\nValuation\nEquity value: ${value:,.1f} million\nShare of value after 2030: {terminal_share:.1%}\nValue per share: ${per_share:,.2f}")


if __name__ == "__main__":
    main()



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

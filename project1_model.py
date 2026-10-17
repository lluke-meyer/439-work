"""Integrated Cadence Design Systems Project 1 finance model.

The model connects the five-year three-statement pro-forma to FCFF and then
discounts those forecast cash flows. It has no user-interface dependency so
it can be tested from the command line and imported by the Streamlit app.
Dollar amounts are USD millions except per-share values.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable


YEARS = (2026, 2027, 2028, 2029, 2030)
VALUATION_DATE = "2026-09-01"
MARKET_PRICE = 313.04

OPENING = {
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
}


@dataclass(frozen=True)
class ModelInputs:
    name: str
    revenue_growth: tuple[float, ...]
    gross_margin: float
    opex_to_gross_profit: tuple[float, ...]
    depreciation_rate: float = 111.4 / 517.004
    annual_capex: float = 142.0
    tax_rate: float = 0.27
    inventory_days: float = 153.5
    deferred_revenue_ratio: float = 934.432 / 5_296.759
    minimum_cash: float = 500.0
    revolver_limit: float = 2_000.0
    revolver_rate: float = 0.05
    debt_repayment: float = 0.0
    annual_share_buyback: float = 900.0
    term_debt_rate: float = 116.541 / 2_476.183
    wacc: float = 0.09
    terminal_growth: float = 0.03
    diluted_shares: float = 273.312


BASE = ModelInputs(
    name="Base",
    revenue_growth=(0.14, 0.12, 0.10, 0.08, 0.05),
    gross_margin=0.865,
    opex_to_gross_profit=(0.670, 0.665, 0.660, 0.655, 0.650),
)

DOWNSIDE = replace(
    BASE,
    name="Downside",
    revenue_growth=(0.11, 0.09, 0.07, 0.05, 0.02),
    gross_margin=0.845,
    opex_to_gross_profit=(0.680, 0.675, 0.670, 0.665, 0.660),
    wacc=0.10,
    terminal_growth=0.025,
)

UPSIDE = replace(
    BASE,
    name="Upside",
    revenue_growth=(0.16, 0.14, 0.12, 0.10, 0.07),
    gross_margin=0.875,
    opex_to_gross_profit=(0.660, 0.655, 0.650, 0.645, 0.640),
    wacc=0.085,
)

SCENARIOS = {item.name: item for item in (DOWNSIDE, BASE, UPSIDE)}


def _validate_inputs(inputs: ModelInputs) -> None:
    if len(inputs.revenue_growth) != len(YEARS):
        raise ValueError("Revenue growth must contain one value for each forecast year.")
    if len(inputs.opex_to_gross_profit) != len(YEARS):
        raise ValueError("Operating-expense ratios must contain one value for each forecast year.")
    if inputs.terminal_growth >= inputs.wacc:
        raise ValueError("Terminal growth must be below WACC.")
    if not 0 < inputs.gross_margin < 1:
        raise ValueError("Gross margin must be between zero and one.")
    if any(growth <= -1 for growth in inputs.revenue_growth):
        raise ValueError("Revenue growth cannot be less than or equal to -100%.")
    if any(not 0 < ratio < 1 for ratio in inputs.opex_to_gross_profit):
        raise ValueError("Operating-expense ratios must be between zero and one.")


def build_proforma(inputs: ModelInputs) -> list[dict[str, float]]:
    """Build articulated income statement, balance sheet, cash flow, and FCFF."""

    _validate_inputs(inputs)
    forecasts: list[dict[str, float]] = []
    opening = OPENING.copy()

    for year, growth, opex_ratio in zip(
        YEARS, inputs.revenue_growth, inputs.opex_to_gross_profit
    ):
        row: dict[str, float] = {"year": float(year)}
        row["revenue"] = opening["revenue"] * (1 + growth)
        row["gross_profit"] = row["revenue"] * inputs.gross_margin
        row["opex"] = row["gross_profit"] * opex_ratio
        row["depreciation"] = opening["ppe"] * inputs.depreciation_rate
        row["operating_income"] = (
            row["gross_profit"] - row["opex"] - row["depreciation"]
        )
        row["interest"] = (
            opening["debt"] * inputs.term_debt_rate
            + opening["revolver"] * inputs.revolver_rate
        )
        row["pretax_income"] = row["operating_income"] - row["interest"]
        row["tax"] = max(0.0, row["pretax_income"]) * inputs.tax_rate
        row["net_income"] = row["pretax_income"] - row["tax"]

        cogs = row["revenue"] - row["gross_profit"]
        row["inventory"] = cogs * inputs.inventory_days / 365
        row["deferred_revenue"] = row["revenue"] * inputs.deferred_revenue_ratio
        row["ppe"] = opening["ppe"] + inputs.annual_capex - row["depreciation"]
        row["other_assets"] = opening["other_assets"]
        row["other_liabilities"] = opening["other_liabilities"]
        row["debt"] = opening["debt"] - inputs.debt_repayment
        row["equity"] = (
            opening["equity"] + row["net_income"] - inputs.annual_share_buyback
        )

        row["inventory_change"] = row["inventory"] - opening["inventory"]
        row["deferred_revenue_change"] = (
            row["deferred_revenue"] - opening["deferred_revenue"]
        )
        row["net_working_capital_change"] = (
            row["inventory_change"] - row["deferred_revenue_change"]
        )
        row["nopat"] = row["operating_income"] * (1 - inputs.tax_rate)
        row["fcff"] = (
            row["nopat"]
            + row["depreciation"]
            - inputs.annual_capex
            - row["net_working_capital_change"]
        )
        row["fcfe"] = (
            row["net_income"]
            + row["depreciation"]
            - inputs.annual_capex
            - row["inventory_change"]
            + row["deferred_revenue_change"]
            - inputs.debt_repayment
        )

        cash_before_revolver = (
            opening["cash"] + row["fcfe"] - inputs.annual_share_buyback
        )
        revolver_change = 0.0
        if cash_before_revolver < inputs.minimum_cash:
            revolver_change = inputs.minimum_cash - cash_before_revolver
            if opening["revolver"] + revolver_change > inputs.revolver_limit:
                raise ValueError(f"FY{year} revolver limit exceeded.")
        elif opening["revolver"] > 0:
            revolver_change = -min(
                opening["revolver"], cash_before_revolver - inputs.minimum_cash
            )
        row["revolver"] = opening["revolver"] + revolver_change
        row["revolver_change"] = revolver_change
        row["cash"] = cash_before_revolver + revolver_change

        assets = row["inventory"] + row["ppe"] + row["other_assets"] + row["cash"]
        claims = (
            row["deferred_revenue"]
            + row["debt"]
            + row["revolver"]
            + row["other_liabilities"]
            + row["equity"]
        )
        row["balance_gap"] = assets - claims
        row["cash_flow_tie_gap"] = row["cash"] - (
            opening["cash"]
            + row["fcfe"]
            - inputs.annual_share_buyback
            + row["revolver_change"]
        )
        row["cash_above_minimum"] = float(
            row["cash"] >= inputs.minimum_cash - 1e-9
        )
        forecasts.append(row)
        opening = row

    return forecasts


def value_fcff(
    forecasts: Iterable[dict[str, float]], inputs: ModelInputs
) -> dict[str, float]:
    """Discount pro-forma FCFF and bridge enterprise value to equity value."""

    _validate_inputs(inputs)
    rows = list(forecasts)
    explicit_pv = sum(
        row["fcff"] / (1 + inputs.wacc) ** year_index
        for year_index, row in enumerate(rows, start=1)
    )
    terminal_value = (
        rows[-1]["fcff"]
        * (1 + inputs.terminal_growth)
        / (inputs.wacc - inputs.terminal_growth)
    )
    terminal_pv = terminal_value / (1 + inputs.wacc) ** len(rows)
    enterprise_value = explicit_pv + terminal_pv
    equity_value = enterprise_value + OPENING["cash"] - OPENING["debt"]
    value_per_share = equity_value / inputs.diluted_shares
    return {
        "explicit_pv": explicit_pv,
        "terminal_value": terminal_value,
        "terminal_pv": terminal_pv,
        "enterprise_value": enterprise_value,
        "cash": OPENING["cash"],
        "debt": OPENING["debt"],
        "equity_value": equity_value,
        "diluted_shares": inputs.diluted_shares,
        "value_per_share": value_per_share,
        "terminal_value_share": terminal_pv / enterprise_value,
    }


def run_model(inputs: ModelInputs) -> dict[str, object]:
    forecasts = build_proforma(inputs)
    valuation = value_fcff(forecasts, inputs)
    checks = {
        "balance_sheets": all(abs(row["balance_gap"]) < 1e-6 for row in forecasts),
        "cash_flow_ties": all(abs(row["cash_flow_tie_gap"]) < 1e-6 for row in forecasts),
        "cash_floor": all(bool(row["cash_above_minimum"]) for row in forecasts),
        "terminal_growth_below_wacc": inputs.terminal_growth < inputs.wacc,
    }
    return {"inputs": inputs, "forecasts": forecasts, "valuation": valuation, "checks": checks}


def run_named_scenarios() -> dict[str, dict[str, object]]:
    return {name: run_model(inputs) for name, inputs in SCENARIOS.items()}


def wacc_growth_grid(inputs: ModelInputs) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for wacc in (0.08, 0.09, 0.10, 0.11):
        for terminal_growth in (0.02, 0.03, 0.04):
            if terminal_growth >= wacc:
                continue
            case = replace(inputs, wacc=wacc, terminal_growth=terminal_growth)
            value = run_model(case)["valuation"]["value_per_share"]
            rows.append(
                {
                    "wacc": wacc,
                    "terminal_growth": terminal_growth,
                    "value_per_share": float(value),
                }
            )
    return rows


def value_with_growth_shift(inputs: ModelInputs, shift: float) -> float:
    shifted = replace(
        inputs,
        revenue_growth=tuple(growth + shift for growth in inputs.revenue_growth),
    )
    return float(run_model(shifted)["valuation"]["value_per_share"])


def implied_uniform_growth_shift(
    inputs: ModelInputs,
    target_price: float = MARKET_PRICE,
    lower: float = -0.20,
    upper: float = 0.50,
) -> float | None:
    """Find the uniform annual revenue-growth shift implied by a target price."""

    lower_value = value_with_growth_shift(inputs, lower)
    upper_value = value_with_growth_shift(inputs, upper)
    if not lower_value <= target_price <= upper_value:
        return None
    for _ in range(100):
        midpoint = (lower + upper) / 2
        midpoint_value = value_with_growth_shift(inputs, midpoint)
        if midpoint_value < target_price:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2


def committee_action(scenario_name: str) -> str:
    if scenario_name == "Downside":
        return "Do not initiate"
    return "Watch/defer - no position at the current market price"


def render_snapshot() -> str:
    results = run_named_scenarios()
    lines = [
        "Cadence Design Systems Project 1 visible output",
        f"Valuation date: {VALUATION_DATE}",
        f"Market price: ${MARKET_PRICE:,.2f}",
        "",
        "Integrated pro-forma FCFF valuation range",
    ]
    for name in ("Downside", "Base", "Upside"):
        result = results[name]
        value = result["valuation"]["value_per_share"]
        checks_pass = all(result["checks"].values())
        lines.append(
            f"{name:<8} ${value:,.2f} per share | checks: "
            f"{'PASS' if checks_pass else 'FAIL'} | action: {committee_action(name)}"
        )

    base = results["Base"]
    lines.extend(
        [
            "",
            "Base-case five-year forecast (USD millions)",
            "Year | Revenue | Operating income | FCFF | Ending cash | Balance gap",
        ]
    )
    for row in base["forecasts"]:
        lines.append(
            f"{int(row['year'])} | {row['revenue']:,.1f} | "
            f"{row['operating_income']:,.1f} | {row['fcff']:,.1f} | "
            f"{row['cash']:,.1f} | {row['balance_gap']:+.6f}"
        )

    valuation = base["valuation"]
    lines.extend(
        [
            "",
            "Base-case enterprise-to-equity bridge",
            f"Enterprise value: ${valuation['enterprise_value']:,.1f} million",
            f"Plus cash: ${valuation['cash']:,.1f} million",
            f"Less debt: ${valuation['debt']:,.1f} million",
            f"Equity value: ${valuation['equity_value']:,.1f} million",
            f"Diluted shares: {valuation['diluted_shares']:,.3f} million",
            f"Value per share: ${valuation['value_per_share']:,.2f}",
            f"Terminal-value share of enterprise value: {valuation['terminal_value_share']:.1%}",
            "",
            "Checks",
        ]
    )
    for check, passed in base["checks"].items():
        lines.append(f"{check}: {'PASS' if passed else 'FAIL'}")

    implied_shift = implied_uniform_growth_shift(BASE)
    lines.extend(
        [
            "",
            "Reverse DCF",
            (
                f"Uniform revenue-growth shift required to reach ${MARKET_PRICE:,.2f}: "
                f"{implied_shift:+.3%} per year"
                if implied_shift is not None
                else "No solution in the tested -20 to +50 percentage-point bracket."
            ),
            "",
            "Comparable-company evidence currently preserved",
            "Synopsys FY2025 P/E: 51.594527x",
            "CDNS implied equity value from that P/E: $209.47 per share",
            "Required enterprise-value peer multiple: pending independent source verification.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshot",
        type=Path,
        help="Write the visible-output snapshot to this path instead of stdout.",
    )
    args = parser.parse_args()
    output = render_snapshot()
    if args.snapshot:
        args.snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.snapshot.write_text(output, encoding="utf-8")
        print(f"Wrote {args.snapshot}")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()

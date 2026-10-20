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

# Sourced WACC building blocks used to make the industry-regime stress explicit.
# The base model still rounds the resulting 10.0115% WACC to 10.0%.
RISK_FREE_RATE = 0.0479
EQUITY_RISK_PREMIUM = 0.0423
BASE_RELEVERED_BETA = 1.2751
PRETAX_DEBT_COST = 0.053804
WACC_TAX_RATE = 0.251084
EQUITY_WEIGHT = 0.972013
DEBT_WEIGHT = 0.027987

# Hexagon D&E facts from Cadence's Q2 2026 Form 10-Q. The operating assumptions
# in AcquisitionInputs below are intentionally separate analyst judgments.
HEXAGON_PURCHASE_CONSIDERATION = 3_101.008
HEXAGON_CASH_CONSIDERATION = 2_200.0
HEXAGON_CASH_ACQUIRED = 154.6
HEXAGON_SHARES_ISSUED = 3.224473
HEXAGON_GOODWILL = 2_147.191
HEXAGON_ACQUIRED_INTANGIBLES = 1_248.0
HEXAGON_INTANGIBLE_LIFE = 7.8
HEXAGON_PRO_FORMA_H1_REVENUE = 3_122.266
CDNS_REPORTED_H1_REVENUE = 3_058.671

# Independently sourced Synopsys EV/TTM-revenue cross-check. Market prices are
# from September 1, 2026; balance-sheet and share inputs are the latest public
# values available before that date. Dollar amounts are USD millions.
SNPS_PRICE = 414.82
SNPS_SHARES = 191.636646
SNPS_CASH_AND_SHORT_TERM_INVESTMENTS = 3_607.669
SNPS_DEBT = 10_037.360
SNPS_TTM_REVENUE = 9_416.465
CDNS_TTM_REVENUE = 5_837.623
CDNS_PEER_BRIDGE_CASH = 1_440.443
CDNS_PEER_BRIDGE_DEBT = 2_482.200
CDNS_PEER_BRIDGE_SHARES = 275.393

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
    wacc: float = 0.10
    terminal_growth: float = 0.03
    diluted_shares: float = 273.312


@dataclass(frozen=True)
class IndustryRegime:
    """Correlated operating and market-risk stress anchored to the base case."""

    name: str
    description: str
    revenue_shift: float
    gross_margin_shift: float
    opex_shift: float
    beta: float


@dataclass(frozen=True)
class AcquisitionInputs:
    """Illustrative incremental Hexagon D&E cash-flow assumptions.

    Starting revenue is a rounded annualization of the Q2 filing's unaudited
    pre-close pro-forma revenue difference. It is not company guidance.
    """

    starting_revenue: float = 440.0
    revenue_growth: tuple[float, ...] = (0.12, 0.10, 0.08, 0.06, 0.04)
    ebita_margin: tuple[float, ...] = (0.14, 0.17, 0.20, 0.22, 0.24)
    synergy_margin: tuple[float, ...] = (0.00, 0.01, 0.02, 0.03, 0.03)
    integration_costs: tuple[float, ...] = (35.0, 25.0, 15.0, 5.0, 0.0)
    capex_ratio: float = 0.03
    net_working_capital_ratio: float = 0.05
    tax_rate: float = 0.27
    wacc: float = 0.105
    terminal_growth: float = 0.03


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
    wacc=0.11,
    terminal_growth=0.025,
)

UPSIDE = replace(
    BASE,
    name="Upside",
    revenue_growth=(0.16, 0.14, 0.12, 0.10, 0.07),
    gross_margin=0.875,
    opex_to_gross_profit=(0.660, 0.655, 0.650, 0.645, 0.640),
    wacc=0.09,
)

SCENARIOS = {item.name: item for item in (DOWNSIDE, BASE, UPSIDE)}

INDUSTRY_REGIMES = (
    IndustryRegime(
        name="AI buildout extends",
        description=(
            "Demand stays strong, but elevated expectations and market sensitivity "
            "keep the discount rate above the base case."
        ),
        revenue_shift=0.03,
        gross_margin_shift=0.005,
        opex_shift=-0.005,
        beta=1.35,
    ),
    IndustryRegime(
        name="Orderly normalization",
        description=(
            "Growth fades along the base path while margin discipline and market "
            "risk remain near the sourced assumptions."
        ),
        revenue_shift=0.00,
        gross_margin_shift=0.000,
        opex_shift=0.000,
        beta=BASE_RELEVERED_BETA,
    ),
    IndustryRegime(
        name="Cycle reversal",
        description=(
            "Customer R&D growth cools, operating leverage weakens, and a higher "
            "beta raises the return demanded for long-duration cash flows."
        ),
        revenue_shift=-0.05,
        gross_margin_shift=-0.020,
        opex_shift=0.010,
        beta=1.50,
    ),
)


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


def _validate_acquisition_inputs(inputs: AcquisitionInputs) -> None:
    for label, values in (
        ("Acquisition revenue growth", inputs.revenue_growth),
        ("Acquisition EBITA margin", inputs.ebita_margin),
        ("Acquisition synergy margin", inputs.synergy_margin),
        ("Acquisition integration costs", inputs.integration_costs),
    ):
        if len(values) != len(YEARS):
            raise ValueError(f"{label} must contain one value for each forecast year.")
    if inputs.starting_revenue <= 0:
        raise ValueError("Acquisition starting revenue must be positive.")
    if inputs.terminal_growth >= inputs.wacc:
        raise ValueError("Acquisition terminal growth must be below acquisition WACC.")
    if not 0 <= inputs.capex_ratio < 1:
        raise ValueError("Acquisition capex ratio must be between zero and one.")
    if not 0 <= inputs.net_working_capital_ratio < 1:
        raise ValueError("Acquisition working-capital ratio must be between zero and one.")
    if any(cost < 0 for cost in inputs.integration_costs):
        raise ValueError("Acquisition integration costs cannot be negative.")


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


def wacc_from_beta(beta: float) -> float:
    """Calculate WACC from the sourced capital structure with a stressed beta."""

    cost_of_equity = RISK_FREE_RATE + beta * EQUITY_RISK_PREMIUM
    return (
        EQUITY_WEIGHT * cost_of_equity
        + DEBT_WEIGHT * PRETAX_DEBT_COST * (1 - WACC_TAX_RATE)
    )


def run_industry_regimes(
    base_inputs: ModelInputs = BASE,
) -> list[dict[str, object]]:
    """Run correlated semiconductor-demand and market-risk regimes."""

    rows: list[dict[str, object]] = []
    for regime in INDUSTRY_REGIMES:
        stressed = replace(
            base_inputs,
            name=regime.name,
            revenue_growth=tuple(
                growth + regime.revenue_shift for growth in base_inputs.revenue_growth
            ),
            gross_margin=base_inputs.gross_margin + regime.gross_margin_shift,
            opex_to_gross_profit=tuple(
                ratio + regime.opex_shift
                for ratio in base_inputs.opex_to_gross_profit
            ),
            wacc=wacc_from_beta(regime.beta),
        )
        result = run_model(stressed)
        rows.append(
            {
                "name": regime.name,
                "description": regime.description,
                "beta": regime.beta,
                "inputs": stressed,
                "result": result,
            }
        )
    return rows


def wacc_growth_grid(inputs: ModelInputs) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for wacc in (0.09, 0.10, 0.11):
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


def comparable_company_evidence() -> dict[str, float]:
    """Return the sourced Synopsys EV/revenue cross-check for CDNS."""

    peer_market_cap = SNPS_PRICE * SNPS_SHARES
    peer_enterprise_value = (
        peer_market_cap + SNPS_DEBT - SNPS_CASH_AND_SHORT_TERM_INVESTMENTS
    )
    peer_ev_to_revenue = peer_enterprise_value / SNPS_TTM_REVENUE
    implied_enterprise_value = peer_ev_to_revenue * CDNS_TTM_REVENUE
    implied_equity_value = (
        implied_enterprise_value
        + CDNS_PEER_BRIDGE_CASH
        - CDNS_PEER_BRIDGE_DEBT
    )
    implied_value_per_share = implied_equity_value / CDNS_PEER_BRIDGE_SHARES
    target_market_cap = MARKET_PRICE * CDNS_PEER_BRIDGE_SHARES
    target_enterprise_value = (
        target_market_cap + CDNS_PEER_BRIDGE_DEBT - CDNS_PEER_BRIDGE_CASH
    )
    target_ev_to_revenue = target_enterprise_value / CDNS_TTM_REVENUE
    return {
        "peer_market_cap": peer_market_cap,
        "peer_enterprise_value": peer_enterprise_value,
        "peer_ev_to_revenue": peer_ev_to_revenue,
        "implied_enterprise_value": implied_enterprise_value,
        "implied_equity_value": implied_equity_value,
        "implied_value_per_share": implied_value_per_share,
        "target_ev_to_revenue": target_ev_to_revenue,
        "target_premium_to_peer_multiple": (
            target_ev_to_revenue / peer_ev_to_revenue - 1
        ),
    }


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


def implied_wacc(
    inputs: ModelInputs,
    target_price: float = MARKET_PRICE,
    lower: float | None = None,
    upper: float = 0.25,
) -> float | None:
    """Solve for the WACC that reconciles the operating case to target price."""

    lower = max(inputs.terminal_growth + 0.0001, 0.0301) if lower is None else lower
    lower_value = float(run_model(replace(inputs, wacc=lower))["valuation"]["value_per_share"])
    upper_value = float(run_model(replace(inputs, wacc=upper))["valuation"]["value_per_share"])
    if not upper_value <= target_price <= lower_value:
        return None
    for _ in range(100):
        midpoint = (lower + upper) / 2
        midpoint_value = float(
            run_model(replace(inputs, wacc=midpoint))["valuation"]["value_per_share"]
        )
        if midpoint_value > target_price:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2


def implied_gross_margin(
    inputs: ModelInputs,
    target_price: float = MARKET_PRICE,
    lower: float = 0.50,
    upper: float = 0.99,
) -> float | None:
    """Solve for the constant gross margin that reconciles to target price."""

    lower_value = float(
        run_model(replace(inputs, gross_margin=lower))["valuation"]["value_per_share"]
    )
    upper_value = float(
        run_model(replace(inputs, gross_margin=upper))["valuation"]["value_per_share"]
    )
    if not lower_value <= target_price <= upper_value:
        return None
    for _ in range(100):
        midpoint = (lower + upper) / 2
        midpoint_value = float(
            run_model(replace(inputs, gross_margin=midpoint))["valuation"]["value_per_share"]
        )
        if midpoint_value < target_price:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2


def market_expectations_dashboard(
    inputs: ModelInputs = BASE,
    target_price: float = MARKET_PRICE,
) -> dict[str, object]:
    """Expose the operating and discount-rate burden embedded in market price."""

    feasibility = []
    for wacc in (0.08, 0.09, 0.10, 0.11, 0.12):
        case = replace(inputs, wacc=wacc)
        growth_shift = implied_uniform_growth_shift(case, target_price=target_price)
        feasibility.append(
            {
                "wacc": wacc,
                "growth_shift": growth_shift,
                "first_year_growth": (
                    inputs.revenue_growth[0] + growth_shift
                    if growth_shift is not None
                    else None
                ),
                "terminal_year_growth": (
                    inputs.revenue_growth[-1] + growth_shift
                    if growth_shift is not None
                    else None
                ),
            }
        )

    bounded = replace(
        inputs,
        name="Bounded operating challenge",
        revenue_growth=tuple(growth + 0.05 for growth in inputs.revenue_growth),
        gross_margin=0.90,
        opex_to_gross_profit=tuple(ratio - 0.03 for ratio in inputs.opex_to_gross_profit),
        wacc=0.08,
        terminal_growth=0.04,
    )
    bounded_result = run_model(bounded)
    bounded_value = float(bounded_result["valuation"]["value_per_share"])
    return {
        "target_price": target_price,
        "base_value": float(run_model(inputs)["valuation"]["value_per_share"]),
        "implied_growth_shift": implied_uniform_growth_shift(
            inputs, target_price=target_price
        ),
        "implied_wacc": implied_wacc(inputs, target_price=target_price),
        "implied_gross_margin": implied_gross_margin(
            inputs, target_price=target_price
        ),
        "feasibility": feasibility,
        "bounded_inputs": bounded,
        "bounded_result": bounded_result,
        "bounded_value": bounded_value,
        "bounded_shortfall": target_price - bounded_value,
    }


def acquisition_overlay(
    base_result: dict[str, object] | None = None,
    inputs: AcquisitionInputs = AcquisitionInputs(),
) -> dict[str, object]:
    """Value Hexagon D&E as a separate incremental cash-flow overlay.

    The base three-statement model remains untouched. The combined per-share
    illustration adjusts pre-deal cash for net cash consideration and adds the
    issued shares, preventing the acquisition from being hidden in base growth.
    """

    _validate_acquisition_inputs(inputs)
    base_result = run_model(BASE) if base_result is None else base_result
    revenue = inputs.starting_revenue
    prior_revenue = revenue
    forecasts: list[dict[str, float]] = []
    for year, growth, margin, synergy_margin, integration_cost in zip(
        YEARS,
        inputs.revenue_growth,
        inputs.ebita_margin,
        inputs.synergy_margin,
        inputs.integration_costs,
    ):
        revenue *= 1 + growth
        ebita = revenue * margin
        synergy = revenue * synergy_margin
        integration_after_tax = integration_cost * (1 - inputs.tax_rate)
        capex = revenue * inputs.capex_ratio
        revenue_change = revenue - prior_revenue
        working_capital_investment = max(0.0, revenue_change) * inputs.net_working_capital_ratio
        fcff = (
            (ebita + synergy) * (1 - inputs.tax_rate)
            - integration_after_tax
            - capex
            - working_capital_investment
        )
        forecasts.append(
            {
                "year": float(year),
                "revenue": revenue,
                "ebita": ebita,
                "synergy": synergy,
                "integration_cost": integration_cost,
                "capex": capex,
                "working_capital_investment": working_capital_investment,
                "fcff": fcff,
            }
        )
        prior_revenue = revenue

    explicit_pv = sum(
        row["fcff"] / (1 + inputs.wacc) ** index
        for index, row in enumerate(forecasts, start=1)
    )
    terminal_value = (
        forecasts[-1]["fcff"]
        * (1 + inputs.terminal_growth)
        / (inputs.wacc - inputs.terminal_growth)
    )
    terminal_pv = terminal_value / (1 + inputs.wacc) ** len(forecasts)
    acquired_enterprise_value = explicit_pv + terminal_pv
    net_cash_paid = HEXAGON_CASH_CONSIDERATION - HEXAGON_CASH_ACQUIRED
    net_purchase_consideration = (
        HEXAGON_PURCHASE_CONSIDERATION - HEXAGON_CASH_ACQUIRED
    )

    base_valuation = base_result["valuation"]
    combined_equity_value = (
        float(base_valuation["enterprise_value"])
        + acquired_enterprise_value
        + float(base_valuation["cash"])
        - float(base_valuation["debt"])
        - net_cash_paid
    )
    combined_shares = float(base_valuation["diluted_shares"]) + HEXAGON_SHARES_ISSUED
    combined_value_per_share = combined_equity_value / combined_shares
    base_value_per_share = float(base_valuation["value_per_share"])
    return {
        "inputs": inputs,
        "forecasts": forecasts,
        "explicit_pv": explicit_pv,
        "terminal_value": terminal_value,
        "terminal_pv": terminal_pv,
        "acquired_enterprise_value": acquired_enterprise_value,
        "purchase_consideration": HEXAGON_PURCHASE_CONSIDERATION,
        "net_purchase_consideration": net_purchase_consideration,
        "net_value_creation": acquired_enterprise_value
        - net_purchase_consideration,
        "net_cash_paid": net_cash_paid,
        "combined_equity_value": combined_equity_value,
        "combined_shares": combined_shares,
        "combined_value_per_share": combined_value_per_share,
        "per_share_effect": combined_value_per_share - base_value_per_share,
        "annual_acquired_amortization": (
            HEXAGON_ACQUIRED_INTANGIBLES / HEXAGON_INTANGIBLE_LIFE
        ),
        "terminal_value_share": terminal_pv / acquired_enterprise_value,
    }


def committee_decision(
    result: dict[str, object],
    market_price: float = MARKET_PRICE,
    margin_of_safety: float = 0.15,
    do_not_initiate_floor_value: float | None = None,
) -> dict[str, object]:
    """Apply disclosed committee rules to the calculated result."""

    checks = result["checks"]
    failed_checks = [name for name, passed in checks.items() if not passed]
    value_per_share = float(result["valuation"]["value_per_share"])
    value_to_price = value_per_share / market_price
    monitoring_floor_value = (
        float(run_model(DOWNSIDE)["valuation"]["value_per_share"])
        if do_not_initiate_floor_value is None
        else do_not_initiate_floor_value
    )
    if failed_checks:
        action = "Stop / escalate"
        rationale = "One or more model-integrity checks failed."
    elif value_per_share >= market_price * (1 + margin_of_safety):
        action = "Initiate"
        rationale = f"Intrinsic value clears the {margin_of_safety:.0%} margin-of-safety rule."
    elif value_per_share <= monitoring_floor_value + 1e-9:
        action = "Do not initiate"
        rationale = (
            "Intrinsic value is at or below the independently modeled downside floor."
        )
    else:
        action = "Watch/defer - no position at the current market price"
        rationale = (
            "The model does not clear the margin-of-safety rule, but remains above "
            "the independently modeled downside floor used for continued monitoring."
        )
    return {
        "action": action,
        "rationale": rationale,
        "value_per_share": value_per_share,
        "value_to_price": value_to_price,
        "market_premium_to_value": market_price / value_per_share - 1,
        "required_initiation_value": market_price * (1 + margin_of_safety),
        "monitoring_floor_value": monitoring_floor_value,
        "failed_checks": failed_checks,
    }


def committee_action(result_or_scenario: dict[str, object] | str) -> str:
    """Backward-compatible action label powered by calculated results."""

    if isinstance(result_or_scenario, str):
        result = run_model(SCENARIOS[result_or_scenario])
    else:
        result = result_or_scenario
    return str(committee_decision(result)["action"])


def render_snapshot() -> str:
    results = run_named_scenarios()
    peer = comparable_company_evidence()
    expectations = market_expectations_dashboard(BASE)
    regimes = run_industry_regimes()
    overlay = acquisition_overlay(results["Base"])
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

    implied_shift = expectations["implied_growth_shift"]
    implied_rate = expectations["implied_wacc"]
    implied_margin = expectations["implied_gross_margin"]
    lines.extend(
        [
            "",
            "Market-implied expectations dashboard",
            (
                f"Uniform revenue-growth shift required to reach ${MARKET_PRICE:,.2f}: "
                f"{implied_shift:+.3%} per year"
                if implied_shift is not None
                else "No solution in the tested -20 to +50 percentage-point bracket."
            ),
            (
                f"WACC required with base operations: {implied_rate:.3%}"
                if implied_rate is not None
                else "No WACC solution in the tested range."
            ),
            (
                f"Gross margin required with base growth and WACC: {implied_margin:.3%}"
                if implied_margin is not None
                else "Gross margin alone cannot reach market price below the 99% test ceiling."
            ),
            (
                "Bounded operating challenge value: "
                f"${expectations['bounded_value']:,.2f} per share | shortfall: "
                f"${expectations['bounded_shortfall']:,.2f}"
            ),
            "WACC | Required growth shift | Implied FY2026/FY2030 growth",
        ]
    )
    for row in expectations["feasibility"]:
        if row["growth_shift"] is None:
            lines.append(f"{row['wacc']:.1%} | no solution | no solution")
        else:
            lines.append(
                f"{row['wacc']:.1%} | {row['growth_shift']:+.3%} | "
                f"{row['first_year_growth']:.1%}/{row['terminal_year_growth']:.1%}"
            )

    lines.extend(["", "Semiconductor industry regimes"])
    for regime in regimes:
        regime_result = regime["result"]
        regime_inputs = regime["inputs"]
        lines.append(
            f"{regime['name']}: beta {regime['beta']:.4f} | "
            f"WACC {regime_inputs.wacc:.3%} | "
            f"value ${regime_result['valuation']['value_per_share']:,.2f} | "
            f"action: {committee_action(regime_result)}"
        )

    lines.extend(
        [
            "",
            "Hexagon D&E acquisition overlay (illustrative; separate from base statements)",
            f"Purchase consideration: ${HEXAGON_PURCHASE_CONSIDERATION:,.1f} million",
            f"Acquired-operation enterprise value: ${overlay['acquired_enterprise_value']:,.1f} million",
            f"Value creation versus net consideration: ${overlay['net_value_creation']:,.1f} million",
            f"Combined illustrative value per share: ${overlay['combined_value_per_share']:,.2f}",
            f"Per-share effect versus standalone base: ${overlay['per_share_effect']:+,.2f}",
            (
                "Boundary: starting revenue, margins, synergies, integration costs, "
                "reinvestment, and acquisition WACC are analyst assumptions."
            ),
            "",
            "Comparable-company evidence",
            "Synopsys FY2025 P/E: 51.594527x",
            "CDNS implied equity value from that P/E: $209.47 per share",
            f"Synopsys EV/TTM revenue: {peer['peer_ev_to_revenue']:.6f}x",
            (
                "CDNS implied equity value from that EV/TTM-revenue multiple: "
                f"${peer['implied_value_per_share']:,.2f} per share"
            ),
            f"CDNS market EV/TTM revenue: {peer['target_ev_to_revenue']:.6f}x",
            (
                "CDNS premium to the Synopsys EV/TTM-revenue multiple: "
                f"{peer['target_premium_to_peer_multiple']:.1%}"
            ),
            (
                "Qualification: the peer bridge uses latest pre-valuation-date "
                "2026 inputs; the integrated DCF retains FY2025 opening balances."
            ),
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

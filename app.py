"""Streamlit interface for the CDNS Project 1 finance system."""

from dataclasses import replace

import streamlit as st

from project1_model import (
    MARKET_PRICE,
    SCENARIOS,
    VALUATION_DATE,
    committee_action,
    implied_uniform_growth_shift,
    run_model,
    run_named_scenarios,
    wacc_growth_grid,
)


st.set_page_config(page_title="CDNS Valuation Workbench", layout="wide")
st.title("Cadence Design Systems Valuation Workbench")
st.caption(
    "FIN 43900 Project 1 | Buy-side committee decision | "
    f"Valuation date {VALUATION_DATE} | USD millions except per-share values"
)

st.info(
    "Committee question: should a fund with no current CDNS position initiate, "
    "watch/defer, or not initiate? The workbench connects the five-year pro-forma "
    "to FCFF and reports a conditional range rather than a single target."
)

scenario_name = st.sidebar.selectbox(
    "Named scenario", ("Base", "Downside", "Upside"), index=0
)
preset = SCENARIOS[scenario_name]

st.sidebar.header("Bounded driver panel")
revenue_shift_pp = st.sidebar.slider(
    "Uniform revenue-growth shift (percentage points)",
    min_value=-5.0,
    max_value=5.0,
    value=0.0,
    step=0.5,
    key=f"revenue_shift_{scenario_name}",
)
gross_margin_pct = st.sidebar.slider(
    "Gross margin",
    min_value=80.0,
    max_value=90.0,
    value=float(round(preset.gross_margin * 100, 1)),
    step=0.1,
    key=f"gross_margin_{scenario_name}",
)
opex_shift_pp = st.sidebar.slider(
    "Operating-expense ratio shift (percentage points)",
    min_value=-3.0,
    max_value=3.0,
    value=0.0,
    step=0.5,
    key=f"opex_shift_{scenario_name}",
)
wacc_pct = st.sidebar.slider(
    "WACC",
    min_value=7.0,
    max_value=13.0,
    value=float(round(preset.wacc * 100, 1)),
    step=0.1,
    key=f"wacc_{scenario_name}",
)
terminal_growth_pct = st.sidebar.slider(
    "Terminal growth",
    min_value=1.0,
    max_value=4.0,
    value=float(round(preset.terminal_growth * 100, 1)),
    step=0.1,
    key=f"terminal_growth_{scenario_name}",
)

inputs = replace(
    preset,
    name=scenario_name,
    revenue_growth=tuple(
        growth + revenue_shift_pp / 100 for growth in preset.revenue_growth
    ),
    gross_margin=gross_margin_pct / 100,
    opex_to_gross_profit=tuple(
        ratio + opex_shift_pp / 100 for ratio in preset.opex_to_gross_profit
    ),
    wacc=wacc_pct / 100,
    terminal_growth=terminal_growth_pct / 100,
)

try:
    result = run_model(inputs)
except ValueError as exc:
    st.error(f"Model stopped: {exc}")
    st.stop()

valuation = result["valuation"]
forecasts = result["forecasts"]
action = committee_action(scenario_name)

st.success(f"Committee action: {action}")
metric_cols = st.columns(4)
metric_cols[0].metric("Intrinsic value", f"${valuation['value_per_share']:,.2f}")
metric_cols[1].metric("Market price", f"${MARKET_PRICE:,.2f}")
metric_cols[2].metric(
    "Market premium to model",
    f"{MARKET_PRICE / valuation['value_per_share'] - 1:.1%}",
)
metric_cols[3].metric(
    "Terminal-value share", f"{valuation['terminal_value_share']:.1%}"
)

st.subheader("Named valuation range")
named_results = run_named_scenarios()
range_rows = []
for name in ("Downside", "Base", "Upside"):
    named = named_results[name]
    range_rows.append(
        {
            "Scenario": name,
            "Value per share": f"${named['valuation']['value_per_share']:,.2f}",
            "WACC": f"{named['inputs'].wacc:.1%}",
            "Terminal growth": f"{named['inputs'].terminal_growth:.1%}",
            "Action": committee_action(name),
            "Checks": "PASS" if all(named["checks"].values()) else "FAIL",
        }
    )
st.dataframe(range_rows, width="stretch", hide_index=True)

st.subheader("Five-year pro-forma and FCFF")
forecast_rows = []
for row in forecasts:
    forecast_rows.append(
        {
            "Year": int(row["year"]),
            "Revenue": round(row["revenue"], 1),
            "Gross profit": round(row["gross_profit"], 1),
            "Operating income": round(row["operating_income"], 1),
            "Net income": round(row["net_income"], 1),
            "FCFF": round(row["fcff"], 1),
            "FCFE": round(row["fcfe"], 1),
            "Ending cash": round(row["cash"], 1),
        }
    )
st.dataframe(forecast_rows, width="stretch", hide_index=True)

bridge_col, checks_col = st.columns(2)
with bridge_col:
    st.subheader("Enterprise-to-equity bridge")
    st.table(
        [
            {"Item": "Enterprise value", "Amount": f"${valuation['enterprise_value']:,.1f} million"},
            {"Item": "Plus: cash", "Amount": f"${valuation['cash']:,.1f} million"},
            {"Item": "Less: debt", "Amount": f"${valuation['debt']:,.1f} million"},
            {"Item": "Equity value", "Amount": f"${valuation['equity_value']:,.1f} million"},
            {"Item": "Diluted shares", "Amount": f"{valuation['diluted_shares']:,.3f} million"},
            {"Item": "Value per share", "Amount": f"${valuation['value_per_share']:,.2f}"},
        ]
    )

with checks_col:
    st.subheader("Fail-loud checks")
    for label, passed in result["checks"].items():
        if passed:
            st.success(f"PASS: {label.replace('_', ' ')}")
        else:
            st.error(f"FAIL: {label.replace('_', ' ')}")
    demonstrate_failure = st.checkbox(
        "Demonstrate an incoherent terminal-growth input",
        help="This does not change the active model. It deliberately tests terminal growth equal to WACC.",
    )
    if demonstrate_failure:
        try:
            run_model(replace(inputs, terminal_growth=inputs.wacc))
        except ValueError as exc:
            st.error(f"EXPECTED FAILURE: {exc}")

st.subheader("WACC-terminal growth sensitivity")
sensitivity_rows = [
    {
        "WACC": f"{row['wacc']:.1%}",
        "Terminal growth": f"{row['terminal_growth']:.1%}",
        "Value per share": f"${row['value_per_share']:,.2f}",
    }
    for row in wacc_growth_grid(SCENARIOS["Base"])
]
st.dataframe(sensitivity_rows, width="stretch", hide_index=True)

st.subheader("Reverse DCF")
implied_shift = implied_uniform_growth_shift(SCENARIOS["Base"])
if implied_shift is None:
    st.warning("No solution in the tested -20 to +50 percentage-point growth bracket.")
else:
    st.write(
        f"Holding the other base inputs fixed, matching ${MARKET_PRICE:,.2f} requires "
        f"adding {implied_shift:.3%} to every annual revenue-growth assumption. "
        "This is a mechanical market-implied result, not a forecast."
    )

st.subheader("Comparable-company evidence")
st.write(
    "Synopsys FY2025 P/E is 51.594527x. Applied to CDNS FY2025 GAAP diluted "
    "EPS of $4.06, it implies $209.47 per share. Synopsys is the only admitted "
    "peer, so this is a reference point rather than a peer range."
)
st.warning(
    "Open requirement: add one independently sourced enterprise-value peer multiple "
    "before freezing the submission. Do not infer it from the P/E result."
)

st.subheader("Assumption-challenge record")
st.dataframe(
    [
        {
            "Driver": "Revenue growth",
            "Base": "14%, 12%, 10%, 8%, 5%",
            "Basis": "FY2025 growth, then maturation fade",
            "Challenge": "Acquired versus organic growth and cyclicality",
            "Evidence that changes it": "Post-acquisition organic growth and backlog conversion",
        },
        {
            "Driver": "Gross margin",
            "Base": "86.5%",
            "Basis": "Normalized FY2025 operating mix assumption",
            "Challenge": "Hardware, IP, and acquisition mix",
            "Evidence that changes it": "Updated segment and product-mix margins",
        },
        {
            "Driver": "Operating expense / gross profit",
            "Base": "67.0% declining to 65.0%",
            "Basis": "FY2025 ratio with gradual operating leverage",
            "Challenge": "R&D needs and integration costs",
            "Evidence that changes it": "Quarterly opex and acquisition-integration disclosures",
        },
        {
            "Driver": "WACC",
            "Base": "9.0%",
            "Basis": "Current model assumption",
            "Challenge": "Capital structure and market-input definitions",
            "Evidence that changes it": "Independently sourced risk-free rate, beta, ERP, debt cost, and weights",
        },
    ],
    width="stretch",
    hide_index=True,
)

st.caption(
    "Educational analysis for FIN 43900. Not investment research or financial advice. "
    "Material AI assistance and independent checks are recorded in docs/validation-and-ai-use.md."
)

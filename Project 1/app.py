"""Streamlit interface for the CDNS Project 1 finance system."""

from dataclasses import replace

import streamlit as st

from project1_model import (
    AcquisitionInputs,
    CDNS_REPORTED_H1_REVENUE,
    HEXAGON_ACQUIRED_INTANGIBLES,
    HEXAGON_CASH_ACQUIRED,
    HEXAGON_CASH_CONSIDERATION,
    HEXAGON_GOODWILL,
    HEXAGON_PRO_FORMA_H1_REVENUE,
    HEXAGON_PURCHASE_CONSIDERATION,
    HEXAGON_SHARES_ISSUED,
    MARKET_PRICE,
    SCENARIOS,
    VALUATION_DATE,
    acquisition_overlay,
    committee_action,
    committee_decision,
    comparable_company_evidence,
    market_expectations_dashboard,
    run_model,
    run_industry_regimes,
    run_named_scenarios,
    wacc_growth_grid,
)


st.set_page_config(page_title="CDNS Valuation Workbench", layout="wide")
st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        border: 1px solid rgba(49, 95, 137, 0.22);
        border-radius: 0.65rem;
        padding: 0.65rem 0.8rem;
        background: rgba(49, 95, 137, 0.035);
    }
    div[data-testid="stMetric"] label {font-weight: 650;}
    </style>
    """,
    unsafe_allow_html=True,
)
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
decision = committee_decision(result)
action = str(decision["action"])

if action == "Initiate":
    st.success(f"Committee action: {action}")
elif action in ("Do not initiate", "Stop / escalate"):
    st.error(f"Committee action: {action}")
else:
    st.warning(f"Committee action: {action}")
st.caption(
    f"Rule applied to the calculated output: {decision['rationale']} "
    f"Initiation requires ${decision['required_initiation_value']:,.2f}; "
    f"continued monitoring requires at least ${decision['monitoring_floor_value']:,.2f}."
)
metric_cols = st.columns(5)
metric_cols[0].metric("Intrinsic value", f"${valuation['value_per_share']:,.2f}")
metric_cols[1].metric("Market price", f"${MARKET_PRICE:,.2f}")
metric_cols[2].metric(
    "Market premium to model",
    f"{MARKET_PRICE / valuation['value_per_share'] - 1:.1%}",
)
metric_cols[3].metric(
    "Terminal-value share", f"{valuation['terminal_value_share']:.1%}"
)
metric_cols[4].metric(
    "Value / market price", f"{decision['value_to_price']:.1%}"
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
            "Action": committee_action(named),
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

st.header("What must be true for the market price to work?")
expectations = market_expectations_dashboard(SCENARIOS["Base"])
implied_shift = expectations["implied_growth_shift"]
implied_rate = expectations["implied_wacc"]
implied_margin = expectations["implied_gross_margin"]

expectation_cols = st.columns(4)
expectation_cols[0].metric(
    "Required annual growth shift",
    f"{implied_shift:+.2%}" if implied_shift is not None else "No solution",
    help="Added to every annual base revenue-growth assumption.",
)
expectation_cols[1].metric(
    "Required WACC",
    f"{implied_rate:.2%}" if implied_rate is not None else "No solution",
    delta=(
        f"{(implied_rate - SCENARIOS['Base'].wacc) * 10_000:+.0f} bp vs. base"
        if implied_rate is not None
        else None
    ),
    delta_color="off",
)
expectation_cols[2].metric(
    "Best bounded challenge",
    f"${expectations['bounded_value']:,.2f}",
    delta=f"-${expectations['bounded_shortfall']:,.2f} vs. market",
    delta_color="inverse",
)
expectation_cols[3].metric(
    "Gross margin alone",
    f"{implied_margin:.1%}" if implied_margin is not None else ">99% / no solution",
)

st.write(
    "The reverse DCF now tests the burden of proof several ways. At the sourced "
    "10.0% WACC, price requires adding the calculated shift to every forecast-year "
    "growth rate. Holding the operating forecast fixed instead requires the displayed "
    "WACC. Even the bounded challenge - +5 points of growth, 90% gross margin, "
    "3 points of expense leverage, 8% WACC, and 4% terminal growth - remains below price."
)

feasibility_rows = []
for row in expectations["feasibility"]:
    feasibility_rows.append(
        {
            "WACC": f"{row['wacc']:.1%}",
            "Required annual growth shift": (
                f"{row['growth_shift']:+.2%}"
                if row["growth_shift"] is not None
                else "No solution"
            ),
            "Implied FY2026 growth": (
                f"{row['first_year_growth']:.1%}"
                if row["first_year_growth"] is not None
                else "-"
            ),
            "Implied FY2030 growth": (
                f"{row['terminal_year_growth']:.1%}"
                if row["terminal_year_growth"] is not None
                else "-"
            ),
        }
    )
st.dataframe(feasibility_rows, width="stretch", hide_index=True)
st.caption(
    "These are mechanical market-implied combinations, not forecasts. The table "
    "makes the interaction between operating expectations and discount-rate risk visible."
)

st.header("Semiconductor-cycle regimes")
st.write(
    "These cases move growth, margins, operating leverage, beta, and WACC together. "
    "That avoids the unrealistic assumption that an extended AI buildout raises cash "
    "flows while leaving market sensitivity unchanged."
)
regime_rows = []
for regime in run_industry_regimes():
    regime_result = regime["result"]
    regime_inputs = regime["inputs"]
    regime_rows.append(
        {
            "Regime": regime["name"],
            "Revenue shift": f"{regime_inputs.revenue_growth[0] - SCENARIOS['Base'].revenue_growth[0]:+.1%}",
            "Gross margin": f"{regime_inputs.gross_margin:.1%}",
            "Beta": f"{regime['beta']:.4f}",
            "WACC": f"{regime_inputs.wacc:.2%}",
            "Value per share": f"${regime_result['valuation']['value_per_share']:,.2f}",
            "Action": committee_action(regime_result),
        }
    )
st.dataframe(regime_rows, width="stretch", hide_index=True)
with st.expander("Regime logic and interpretation"):
    for regime in run_industry_regimes():
        st.markdown(f"**{regime['name']}:** {regime['description']}")

st.header("Hexagon D&E acquisition overlay")
st.write(
    "The transaction is modeled as a separate incremental layer so the FY2025-based "
    "statements stay auditable. Filing facts and analyst assumptions are shown separately."
)

fact_cols = st.columns(4)
fact_cols[0].metric("Purchase consideration", f"${HEXAGON_PURCHASE_CONSIDERATION:,.0f}M")
fact_cols[1].metric("Cash consideration", f"${HEXAGON_CASH_CONSIDERATION:,.0f}M")
fact_cols[2].metric("Shares issued", f"{HEXAGON_SHARES_ISSUED:.3f}M")
fact_cols[3].metric("Goodwill + intangibles", f"${HEXAGON_GOODWILL + HEXAGON_ACQUIRED_INTANGIBLES:,.0f}M")

with st.expander("Change acquisition assumptions", expanded=False):
    acq_control_cols = st.columns(5)
    with acq_control_cols[0]:
        acq_revenue = st.number_input(
            "Starting revenue ($M)", 250.0, 750.0, 440.0, 10.0
        )
    with acq_control_cols[1]:
        acq_terminal_margin = st.slider(
            "FY2030 EBITA margin", 10.0, 35.0, 24.0, 1.0
        )
    with acq_control_cols[2]:
        acq_synergy = st.slider("FY2030 synergy margin", 0.0, 6.0, 3.0, 0.5)
    with acq_control_cols[3]:
        acq_integration = st.number_input(
            "FY2026 integration cost ($M)", 0.0, 125.0, 35.0, 5.0
        )
    with acq_control_cols[4]:
        acq_wacc = st.slider("Acquisition WACC", 8.0, 14.0, 10.5, 0.1)

margin_start = max(0.05, acq_terminal_margin / 100 - 0.10)
margin_step = (acq_terminal_margin / 100 - margin_start) / 4
acq_inputs = AcquisitionInputs(
    starting_revenue=acq_revenue,
    ebita_margin=tuple(margin_start + margin_step * index for index in range(5)),
    synergy_margin=(
        0.0,
        acq_synergy / 300,
        acq_synergy / 150,
        acq_synergy / 100,
        acq_synergy / 100,
    ),
    integration_costs=(
        acq_integration,
        acq_integration * 5 / 7,
        acq_integration * 3 / 7,
        acq_integration / 7,
        0.0,
    ),
    wacc=acq_wacc / 100,
)
overlay = acquisition_overlay(run_model(SCENARIOS["Base"]), acq_inputs)

overlay_cols = st.columns(4)
overlay_cols[0].metric(
    "Acquired-operation EV", f"${overlay['acquired_enterprise_value']:,.0f}M"
)
overlay_cols[1].metric(
    "Value vs. net consideration", f"${overlay['net_value_creation']:+,.0f}M"
)
overlay_cols[2].metric(
    "Combined illustrative value", f"${overlay['combined_value_per_share']:,.2f}"
)
overlay_cols[3].metric(
    "Per-share acquisition effect", f"${overlay['per_share_effect']:+,.2f}"
)

st.dataframe(
    [
        {
            "Year": int(row["year"]),
            "Revenue": round(row["revenue"], 1),
            "EBITA": round(row["ebita"], 1),
            "Synergy": round(row["synergy"], 1),
            "Integration cost": round(row["integration_cost"], 1),
            "Capex": round(row["capex"], 1),
            "Incremental FCFF": round(row["fcff"], 1),
        }
        for row in overlay["forecasts"]
    ],
    width="stretch",
    hide_index=True,
)
st.caption(
    f"The $440M starting point is a rounded annualization of the unaudited pre-close "
    f"revenue difference between H1 pro forma revenue of ${HEXAGON_PRO_FORMA_H1_REVENUE / 1_000:,.3f}B "
    f"and reported revenue of ${CDNS_REPORTED_H1_REVENUE / 1_000:,.3f}B. Cadence warns that "
    f"the pro forma information is not predictive. The overlay subtracts net cash paid "
    f"(${HEXAGON_CASH_CONSIDERATION - HEXAGON_CASH_ACQUIRED:,.1f}M), adds issued shares, "
    "and treats revenue, EBITA margin, synergies, integration costs, reinvestment, and "
    "the acquisition WACC as adjustable analyst assumptions. It is not merged into the "
    "base statements or presented as company guidance."
)

st.subheader("Comparable-company evidence")
peer = comparable_company_evidence()
st.write(
    "Synopsys FY2025 P/E is 51.594527x. Applied to CDNS FY2025 GAAP diluted "
    "EPS of $4.06, it implies $209.47 per share. Synopsys is the only admitted "
    "peer, so this is a reference point rather than a peer range."
)
st.write(
    f"Synopsys EV/TTM revenue is {peer['peer_ev_to_revenue']:.4f}x. Applied to "
    f"CDNS TTM revenue and the June 2026 CDNS cash/debt/share bridge, it implies "
    f"${peer['implied_value_per_share']:,.2f} per share. CDNS traded at "
    f"{peer['target_ev_to_revenue']:.2f}x, a "
    f"{peer['target_premium_to_peer_multiple']:.1%} premium to the peer multiple."
)
st.caption(
    "This is a qualified single-peer cross-check. Synopsys includes Ansys, and the "
    "peer calculation uses the latest pre-valuation-date 2026 bridge while the "
    "integrated DCF retains FY2025 opening balances. The methods are not averaged."
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
            "Base": "10.0%",
            "Basis": "4.79% Treasury yield, 4.23% ERP, 1.2751 relevered beta, and market weights",
            "Challenge": "Industry beta and recent effective debt-cost proxy",
            "Evidence that changes it": "New Treasury, ERP, beta, borrowing-cost, or capital-structure evidence",
        },
        {
            "Driver": "Semiconductor regime",
            "Base": "Orderly normalization",
            "Basis": "Correlated growth, margin, beta, and WACC stress",
            "Challenge": "The exact beta response cannot be observed in advance",
            "Evidence that changes it": "Quarterly end-market growth, backlog conversion, and updated beta evidence",
        },
        {
            "Driver": "Hexagon overlay",
            "Base": "$440M starting revenue; 24% FY2030 EBITA margin; 10.5% WACC",
            "Basis": "Filing-derived revenue starting point plus labeled analyst assumptions",
            "Challenge": "No standalone company forecast or complete acquired cash-flow history",
            "Evidence that changes it": "Organic/acquired revenue, margin, synergy, integration, and reinvestment disclosures",
        },
        {
            "Driver": "Committee decision rule",
            "Base": "15% initiation margin; $57.20 modeled downside floor",
            "Basis": "Predeclared triage rules applied to calculated value and model checks",
            "Challenge": "Thresholds are policy judgments, not valuation facts",
            "Evidence that changes it": "Committee risk mandate or a documented threshold revision",
        },
    ],
    width="stretch",
    hide_index=True,
)

st.caption(
    "Educational analysis for FIN 43900. Not investment research or financial advice. "
    "Material AI assistance and independent checks are recorded in docs/validation-and-ai-use.md."
)

"""Streamlit interface for the FIN 439 Project 2 portfolio prototype."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from backtest import (
    DEFAULT_BILLS_RETURN_PERCENT,
    DEFAULT_LAG_MONTHS,
    DEFAULT_SWITCH_COST_PERCENT,
    run_backtest,
)
from portfolio import (
    ASSETS,
    CORRELATIONS,
    EXPECTED_RETURNS,
    OBJECTIVE_RETURN,
    RESERVE_ELIGIBLE,
    RESERVE_MINIMUM,
    VOLATILITIES,
    covariance_matrix,
    equal_weight,
    estimate_from_prices,
    inverse_volatility,
    portfolio_result,
    risk_level_portfolios,
    search_lowest_risk_mix,
)


st.set_page_config(page_title="Project 2 Portfolio Decision", layout="wide")
st.title("Project 2 Portfolio Decision")
st.caption("Built with AI help, a learning demonstration, not investment advice.")

with st.sidebar:
    st.header("Mandate controls")
    objective = st.number_input(
        "Objective return (%)", min_value=-25.0, max_value=50.0, value=OBJECTIVE_RETURN * 100, step=0.1
    ) / 100
    reserve_minimum = st.number_input(
        "Reserve minimum (%)", min_value=0.0, max_value=100.0, value=RESERVE_MINIMUM * 100, step=1.0
    ) / 100
    uploaded = st.file_uploader("Upload prices.csv", type="csv")
    classroom_inputs = st.checkbox(
        "Use Meridian classroom inputs instead of bundled prices",
        value=False,
        disabled=uploaded is not None,
    )
    last_36 = st.toggle(
        "Use last 36 monthly returns",
        value=False,
        disabled=uploaded is None and classroom_inputs,
    )
    st.subheader("Signal controls")
    signal_lag = st.number_input(
        "Signal lag (months)", min_value=0, max_value=1, value=DEFAULT_LAG_MONTHS, step=1
    )
    switch_cost = st.number_input(
        "Switch cost (%)", min_value=0.0, max_value=5.0, value=DEFAULT_SWITCH_COST_PERCENT, step=0.05
    )
    bills_return = st.number_input(
        "Bills return (%)", min_value=-10.0, max_value=10.0,
        value=DEFAULT_BILLS_RETURN_PERCENT, step=0.05
    )

if uploaded is None and classroom_inputs:
    assets = ASSETS
    loaded_expected = EXPECTED_RETURNS
    loaded_volatility = VOLATILITIES
    loaded_correlation = CORRELATIONS
    current_expected_defaults = EXPECTED_RETURNS
    current_volatility = VOLATILITIES
    current_correlation = CORRELATIONS
    default_reserve = RESERVE_ELIGIBLE
    source_label = "Meridian training inputs"
    observation_label = "Course-authored inputs"
else:
    try:
        price_source = uploaded if uploaded is not None else Path(__file__).with_name("prices.csv")
        loaded_estimate = estimate_from_prices(price_source, last_36=False)
        current_estimate = estimate_from_prices(price_source, last_36=last_36)
    except (OSError, ValueError) as error:
        st.error(str(error))
        st.stop()
    assets = loaded_estimate["assets"]
    loaded_expected = loaded_estimate["expected_returns"]
    loaded_volatility = loaded_estimate["volatilities"]
    loaded_correlation = loaded_estimate["correlations"]
    current_expected_defaults = current_estimate["expected_returns"]
    current_volatility = current_estimate["volatilities"]
    current_correlation = current_estimate["correlations"]
    default_reserve = tuple(asset.upper() == "TLT" for asset in assets)
    source_label = "Uploaded fund universe" if uploaded is not None else "Bundled six-fund universe"
    observation_label = (
        f"{current_estimate['return_observations']} monthly returns, "
        f"{current_estimate['start_date']} through {current_estimate['end_date']}"
    )

st.subheader(source_label)
st.write(observation_label)
if not classroom_inputs or uploaded is not None:
    st.warning(
        "The 6.5% return objective and 3% reserve threshold are classroom controls, not a full "
        "Project 2 mandate verdict. TLT is a long-duration Treasury fund, not a cash reserve."
    )
st.write("Edit an expected-return estimate or change reserve eligibility to test the allocation.")

header = st.columns([1.7, 1.2, 1.2, 1.3])
header[0].markdown("**Asset**")
header[1].markdown("**Expected return**")
header[2].markdown("**Volatility**")
header[3].markdown("**Reserve eligible**")

edited_expected: list[float] = []
reserve_flags: list[bool] = []
universe_key = "_".join(assets)
for index, asset in enumerate(assets):
    columns = st.columns([1.7, 1.2, 1.2, 1.3])
    columns[0].write(asset)
    edited_expected.append(
        columns[1].number_input(
            f"{asset} expected return (%)",
            min_value=-100.0,
            max_value=200.0,
            value=float(current_expected_defaults[index] * 100),
            step=0.1,
            format="%.2f",
            key=f"return_{universe_key}_{asset}_{'36' if last_36 else 'all'}",
            label_visibility="collapsed",
        )
        / 100
    )
    columns[2].write(f"{current_volatility[index]:.2%}")
    reserve_flags.append(
        columns[3].checkbox(
            f"{asset} is reserve eligible",
            value=default_reserve[index],
            key=f"reserve_{universe_key}_{asset}",
            label_visibility="collapsed",
        )
    )

current_covariance = covariance_matrix(current_volatility, current_correlation)
loaded_covariance = covariance_matrix(loaded_volatility, loaded_correlation)
current_risk_levels = risk_level_portfolios(
    edited_expected, current_covariance, objective, reserve_flags, reserve_minimum
)
current_result = current_risk_levels[0] if current_risk_levels else None
loaded_result = search_lowest_risk_mix(
    loaded_expected, loaded_covariance, objective, reserve_flags, reserve_minimum
)


def mandate_verdict(result: dict[str, object]) -> str:
    return "PASS" if (
        result["expected_return"] >= objective - 1e-12
        and result["reserve_weight"] >= reserve_minimum - 1e-12
    ) else "FAIL"


baseline_results = [
    ("Equal weight", portfolio_result(equal_weight(len(assets)), current_expected_defaults, current_covariance, reserve_flags)),
    ("Inverse volatility", portfolio_result(inverse_volatility(current_volatility), current_expected_defaults, current_covariance, reserve_flags)),
]
if current_result is not None:
    baseline_results.insert(0, ("Constrained search", current_result))


def show_result(container: st.delta_generator.DeltaGenerator, title: str, result: dict[str, object] | None) -> None:
    container.markdown(f"### {title}")
    if result is None:
        container.warning("No mix meets the objective.")
        return
    container.dataframe(
        [
            {"Asset": asset, "Weight": f"{weight:.2%}"}
            for asset, weight in zip(assets, result["weights"])
        ],
        hide_index=True,
        width="stretch",
    )
    metrics = container.columns(3)
    metrics[0].metric("Return", f"{result['expected_return']:.2%}")
    metrics[1].metric("Volatility", f"{result['volatility']:.2%}")
    metrics[2].metric("Reserve", f"{result['reserve_weight']:.2%}")
    weights = result["weights"]
    largest_index = max(range(len(weights)), key=weights.__getitem__)
    active_assets = [asset for asset, weight in zip(assets, weights) if weight > 0.001]
    return_cushion = result["expected_return"] - objective
    reserve_cushion = result["reserve_weight"] - reserve_minimum
    with container.expander("What this result means"):
        st.write(
            f"**Main holding:** {assets[largest_index]} at {weights[largest_index]:.0%}. "
            f"The optimizer uses {len(active_assets)} of {len(assets)} available funds: "
            f"{', '.join(active_assets)}."
        )
        st.write(
            f"**Constraint cushion:** expected return is {return_cushion:.2%} above the objective, "
            f"and reserve weight is {reserve_cushion:.2%} above the minimum."
        )
        st.caption(
            "Volatility is an annualized estimate from monthly returns. A zero weight does not "
            "mean a fund is bad; it means that fund did not improve the lowest-risk feasible mix "
            "under these estimates and 5-point allocation steps."
        )


current_column, loaded_column = st.columns(2)
show_result(current_column, "Current estimates", current_result)
show_result(loaded_column, "Inputs as loaded", loaded_result)

st.subheader("Baseline and mandate verdicts")
st.caption("PASS means the displayed portfolio meets the current objective and reserve controls.")
st.dataframe(
    [
        {
            "Portfolio": name,
            "Return": f"{result['expected_return']:.2%}",
            "Volatility": f"{result['volatility']:.2%}",
            "Reserve": f"{result['reserve_weight']:.2%}",
            "Mandate verdict": mandate_verdict(result),
        }
        for name, result in baseline_results
    ],
    hide_index=True,
    width="stretch",
)

st.subheader("Signal holdout and cost controls")
locked_backtest = run_backtest()
adjusted_backtest = run_backtest(
    lag_months=int(signal_lag),
    switch_cost_percent=float(switch_cost),
    bills_return_percent=float(bills_return),
)
st.caption(
    "The frozen result uses the one-month lag, 0.10% switch cost, and 0.30% bills return. "
    "Sidebar controls run bounded sensitivity scenarios; they do not retune the holdout."
)
backtest_columns = st.columns(2)
for container, title, result in (
    (backtest_columns[0], "Frozen classroom rule", locked_backtest),
    (backtest_columns[1], "Adjusted sensitivity", adjusted_backtest),
):
    container.markdown(f"### {title}")
    development = result["development"]
    holdout = result["holdout"]
    container.dataframe(
        [
            {
                "Period": "Development",
                "Rule gross": f"{development['gross']:.2%}",
                "Rule net": f"{development['net']:.2%}",
                "Buy-and-hold": f"{development['buy_and_hold']:.2%}",
                "Switches": development["switches"],
            },
            {
                "Period": "Holdout",
                "Rule gross": f"{holdout['gross']:.2%}",
                "Rule net": f"{holdout['net']:.2%}",
                "Buy-and-hold": f"{holdout['buy_and_hold']:.2%}",
                "Switches": holdout["switches"],
            },
        ],
        hide_index=True,
        width="stretch",
    )
    if result["failure_triggered"]:
        container.warning("Failure rule triggered: holdout net trails buy-and-hold.")
    else:
        container.success("Failure rule not triggered.")

if current_result is not None:
    current_mandate_passes = mandate_verdict(current_result) == "PASS"
    holdout_passes = not adjusted_backtest["failure_triggered"]
    if current_mandate_passes and holdout_passes:
        st.success("Current process verdict: pilot candidate, subject to final mandate and evidence review.")
    else:
        st.warning("Current process verdict: do not adopt yet; a mandate or holdout check fails under the displayed controls.")

universe_notes = {
    "TLT": "TLT holds long-duration U.S. Treasuries, so it can move sharply when interest-rate expectations change; it is not a cash substitute.",
    "SOXX": "SOXX concentrates on semiconductor companies, adding sector and technology-cycle risk beyond a broad stock-market fund.",
    "GBTC": "GBTC provides spot-Bitcoin exposure and can be highly volatile; its presence in the universe does not require the optimizer to hold it.",
}
relevant_notes = [note for asset, note in universe_notes.items() if asset in assets]
if relevant_notes:
    with st.expander("Risk notes for this fund universe"):
        for note in relevant_notes:
            st.write(f"- {note}")

st.subheader("Risk portfolio allocations: Levels 1–5")
st.caption(
    "These use the current estimates and controls. Every displayed portfolio meets the return "
    "objective and reserve minimum."
)
if not current_risk_levels:
    st.warning("No risk-level portfolios meet the current mandate.")
else:
    profile_names = (
        "Lowest feasible risk",
        "Lower-middle risk",
        "Middle risk",
        "Higher risk",
        "Highest-return efficient",
    )
    st.dataframe(
        [
            {
                "Risk level": level,
                "Profile": profile_names[level - 1],
                "Allocation": " · ".join(
                    f"{asset} {weight:.0%}"
                    for asset, weight in zip(assets, result["weights"])
                    if weight > 0.001
                ),
                "Return": f"{result['expected_return']:.2%}",
                "Volatility": f"{result['volatility']:.2%}",
                "Reserve": f"{result['reserve_weight']:.2%}",
            }
            for level, result in enumerate(current_risk_levels, start=1)
        ],
        hide_index=True,
        width="stretch",
    )
    with st.expander("How the five risk levels are selected"):
        st.write(
            "The engine tests long-only allocations in 5-point steps, removes portfolios that "
            "miss the return objective or reserve minimum, and keeps only efficient choices—ones "
            "not beaten by another mix with lower risk and equal or higher return. Levels 1–5 are "
            "evenly sampled along that efficient frontier."
        )

if current_result is not None and loaded_result is not None:
    changes = [
        abs(current - loaded) * 100
        for current, loaded in zip(current_result["weights"], loaded_result["weights"])
    ]
    largest_index = max(range(len(changes)), key=changes.__getitem__)
    st.metric("Largest weight change", f"{changes[largest_index]:.0f} points", assets[largest_index])
    with st.expander("Why the two allocations can differ"):
        st.write(
            "The left result uses the currently selected return window and any estimates you "
            "edited. The right result keeps the full-history estimates that were loaded from the "
            "CSV. A large weight change shows that the decision is sensitive to the changed "
            "assumptions, not that either estimate is certain."
        )



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

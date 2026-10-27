"""Streamlit interface for the FIN 439 Lab 15 portfolio engine."""

from __future__ import annotations

import streamlit as st

from portfolio import (
    ASSETS,
    CORRELATIONS,
    EXPECTED_RETURNS,
    OBJECTIVE_RETURN,
    RESERVE_ELIGIBLE,
    RESERVE_MINIMUM,
    VOLATILITIES,
    covariance_matrix,
    estimate_from_prices,
    risk_level_portfolios,
    search_lowest_risk_mix,
)


st.set_page_config(page_title="Portfolio Stability Decision", layout="wide")
st.title("Portfolio Stability Decision")
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
    last_36 = st.toggle("Use last 36 monthly returns", value=False, disabled=uploaded is None)

if uploaded is None:
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
        loaded_estimate = estimate_from_prices(uploaded, last_36=False)
        current_estimate = estimate_from_prices(uploaded, last_36=last_36)
    except ValueError as error:
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
    source_label = "Uploaded fund universe"
    observation_label = (
        f"{current_estimate['return_observations']} monthly returns, "
        f"{current_estimate['start_date']} through {current_estimate['end_date']}"
    )

st.subheader(source_label)
st.write(observation_label)
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

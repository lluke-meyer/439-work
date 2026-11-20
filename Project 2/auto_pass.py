"""Find a numerical allocation without silently weakening risk controls."""

from __future__ import annotations

import math
from typing import Iterable

from portfolio import _allocation_units, portfolio_max_drawdown, portfolio_result


def usable_return_target(current_target: float, attainable_return: float) -> float:
    """Keep the target or round an unattainable target down to a 0.1-point input."""
    if attainable_return + 1e-12 >= current_target:
        return current_target
    return math.floor(attainable_return * 1000 + 1e-9) / 1000


def best_numerical_mix(
    *,
    assets: Iterable[str],
    expected_returns: Iterable[float],
    covariance: Iterable[Iterable[float]],
    reserve_eligible: Iterable[bool],
    overlap_groups: Iterable[str],
    correlation: Iterable[Iterable[float]],
    monthly_returns: dict[str, Iterable[float]] | None,
    reserve_floor: float,
    ticker_cap: float,
    bitcoin_cap: float,
    bucket_cap: float,
    pair_cap: float,
    correlation_threshold: float,
    drawdown_tolerance: float,
    allow_shorting: bool,
    short_allowance: float,
    gross_cap: float,
    step: float,
) -> dict[str, object] | None:
    """Maximize scenario return, then minimize volatility, on the displayed grid.

    The selected fund universe and all reserve and risk controls stay fixed. The
    caller may lower only the return target to this mix's attainable return.
    """
    assets = tuple(assets)
    expected = tuple(float(value) for value in expected_returns)
    eligible = tuple(bool(value) for value in reserve_eligible)
    groups = tuple(overlap_groups)
    matrix = tuple(tuple(float(value) for value in row) for row in covariance)
    correlations = tuple(tuple(float(value) for value in row) for row in correlation)
    count = len(assets)
    if not count or any(len(values) != count for values in (expected, eligible, groups, matrix, correlations)):
        raise ValueError("Auto-Pass inputs must align with the selected funds")
    if any(len(row) != count for row in (*matrix, *correlations)):
        raise ValueError("Auto-Pass covariance and correlation must be square")
    if monthly_returns is None or any(asset not in monthly_returns for asset in assets):
        raise ValueError("Observed monthly history is required for the drawdown screen")
    history = {asset: monthly_returns[asset] for asset in assets}
    if reserve_floor > 0 and not any(eligible):
        return None

    group_indices: dict[str, list[int]] = {}
    for index, group in enumerate(groups):
        group_indices.setdefault(group, []).append(index)
    correlated_pairs = tuple(
        (left, right)
        for left in range(count)
        for right in range(left + 1, count)
        if correlations[left][right] >= correlation_threshold
    )
    caps = tuple(min(ticker_cap, bitcoin_cap if asset == "FBTC" else ticker_cap) for asset in assets)
    units_total = round(1.0 / step)
    best: dict[str, object] | None = None
    for units in _allocation_units(
        count, units_total, step, allow_shorting, short_allowance, ticker_cap, gross_cap
    ):
        weights = tuple(unit / units_total for unit in units)
        if any(weight > cap + 1e-12 for weight, cap in zip(weights, caps)):
            continue
        if sum(max(weight, 0.0) for weight, flag in zip(weights, eligible) if flag) + 1e-12 < reserve_floor:
            continue
        if any(sum(abs(weights[index]) for index in indices) > bucket_cap + 1e-12 for indices in group_indices.values()):
            continue
        if any(
            weights[left] > 1e-12 and weights[right] > 1e-12
            and weights[left] + weights[right] > pair_cap + 1e-12
            for left, right in correlated_pairs
        ):
            continue
        scenario_return = sum(weight * rate for weight, rate in zip(weights, expected))
        if best is not None and scenario_return < best["expected_return"] - 1e-12:
            continue
        drawdown = portfolio_max_drawdown(weights, history)
        if drawdown > drawdown_tolerance + 1e-12:
            continue
        result = portfolio_result(weights, expected, matrix, eligible)
        if (
            best is None
            or scenario_return > best["expected_return"] + 1e-12
            or (abs(scenario_return - best["expected_return"]) <= 1e-12 and result["volatility"] < best["volatility"] - 1e-12)
        ):
            best = {**result, "drawdown": drawdown}
    return best

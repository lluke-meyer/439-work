"""Reverse mandate limits for a fixed, user-chosen portfolio composition."""

from __future__ import annotations

import math
from typing import Iterable

from portfolio import (
    OVERLAP_CORRELATION_THRESHOLD,
    overlap_bucket_weights,
    pairwise_overlap_rows,
    portfolio_max_drawdown,
    portfolio_result,
)


def mandate_boundaries(
    weights: Iterable[float],
    assets: Iterable[str],
    expected_returns: Iterable[float],
    covariance: Iterable[Iterable[float]],
    reserve_eligible: Iterable[bool],
    overlap_groups: Iterable[str],
    correlation: Iterable[Iterable[float]],
    monthly_returns: dict[str, Iterable[float]] | None,
    correlation_threshold: float = OVERLAP_CORRELATION_THRESHOLD,
) -> dict[str, object]:
    """Return exact numerical mandate boundaries for the supplied fixed weights.

    No search or parameter relaxation is performed. REVIEW evidence is never
    converted into PASS by this calculation.
    """
    weights = tuple(float(value) for value in weights)
    assets = tuple(assets)
    expected_returns = tuple(float(value) for value in expected_returns)
    reserve_eligible = tuple(bool(value) for value in reserve_eligible)
    overlap_groups = tuple(overlap_groups)
    if not assets or len({len(weights), len(assets), len(expected_returns), len(reserve_eligible), len(overlap_groups)}) != 1:
        raise ValueError("Weights, funds, assumptions, reserve flags, and groups must align")
    if any(not math.isfinite(value) for value in weights) or not math.isclose(sum(weights), 1.0, abs_tol=1e-9):
        raise ValueError("Chosen weights must be finite and total 100%")
    result = portfolio_result(weights, expected_returns, covariance, reserve_eligible)
    buckets = overlap_bucket_weights(weights, overlap_groups, gross=True)
    pair_rows = pairwise_overlap_rows(weights, assets, correlation, correlation_threshold)
    drawdown = (
        portfolio_max_drawdown(weights, monthly_returns)
        if monthly_returns is not None and all(asset in monthly_returns for asset in assets)
        else None
    )
    return {
        "expected_return": result["expected_return"],
        "volatility": result["volatility"],
        "maximum_return_target": result["expected_return"],
        "maximum_reserve_floor": result["reserve_weight"],
        "minimum_ticker_cap": max(max(weights), 0.0),
        "minimum_bitcoin_cap": max((max(weight, 0.0) for asset, weight in zip(assets, weights) if asset == "FBTC"), default=0.0),
        "minimum_short_allowance": max(-min(weights), 0.0),
        "minimum_gross_cap": sum(abs(weight) for weight in weights),
        "minimum_bucket_cap": max(buckets.values()),
        "minimum_pair_cap": max((float(row["Combined weight"]) for row in pair_rows), default=0.0),
        "minimum_drawdown_tolerance": drawdown,
        "binding_bucket": max(buckets, key=buckets.get),
        "binding_pair": str(max(pair_rows, key=lambda row: float(row["Combined weight"]))["Pair"]) if pair_rows else "None at threshold",
    }


def numerical_mandate_pass(boundaries: dict[str, object], limits: dict[str, float]) -> bool:
    """Check the fixed mix against displayed numerical controls only."""
    if boundaries["minimum_drawdown_tolerance"] is None:
        return False
    return all((
        limits["return_target"] <= boundaries["maximum_return_target"] + 1e-12,
        limits["reserve_floor"] <= boundaries["maximum_reserve_floor"] + 1e-12,
        limits["ticker_cap"] + 1e-12 >= boundaries["minimum_ticker_cap"],
        limits["bitcoin_cap"] + 1e-12 >= boundaries["minimum_bitcoin_cap"],
        limits["short_allowance"] + 1e-12 >= boundaries["minimum_short_allowance"],
        limits["gross_cap"] + 1e-12 >= boundaries["minimum_gross_cap"],
        limits["bucket_cap"] + 1e-12 >= boundaries["minimum_bucket_cap"],
        limits["pair_cap"] + 1e-12 >= boundaries["minimum_pair_cap"],
        limits["drawdown_tolerance"] + 1e-12 >= boundaries["minimum_drawdown_tolerance"],
    ))

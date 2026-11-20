"""FIN 439 Project 2 portfolio engine and price-history estimates."""

from __future__ import annotations

import csv
import io
import math
from pathlib import Path
from statistics import mean, stdev
from typing import BinaryIO, Iterable, TextIO


ASSETS = (
    "Treasury bills",
    "Treasury 10-year note",
    "Investment-grade bond fund",
    "Global equity index fund",
)
EXPECTED_RETURNS = (0.035, 0.043, 0.050, 0.080)
VOLATILITIES = (0.005, 0.070, 0.060, 0.160)
CORRELATIONS = (
    (1.00, 0.10, 0.05, 0.00),
    (0.10, 1.00, 0.80, -0.10),
    (0.05, 0.80, 1.00, 0.25),
    (0.00, -0.10, 0.25, 1.00),
)
OBJECTIVE_RETURN = 0.09
RESERVE_ELIGIBLE = (True, True, False, False)
RESERVE_MINIMUM = 0.01
MAX_TICKER_WEIGHT = 0.40
MAX_BITCOIN_WEIGHT = 0.10
MAX_SHORT_WEIGHT = 0.10
MAX_GROSS_EXPOSURE = 1.10
MAX_OVERLAP_WEIGHT = 0.60
MAX_PAIRWISE_OVERLAP_WEIGHT = 0.70
OVERLAP_CORRELATION_THRESHOLD = 0.70
# A 30% review trigger fits the requested moderately risky/risky posture. It is
# still a pause-and-review control, not an automatic liquidation rule.
MAX_DRAWDOWN = 0.30
TURNOVER_LIMIT = 0.25
CLASSROOM_OBJECTIVE_RETURN = 0.065
CLASSROOM_RESERVE_MINIMUM = 0.03

OVERLAP_GROUPS = {
    "VOO": "U.S. equity beta", "VTI": "U.S. equity beta",
    "VNQ": "Real estate equity", "VWO": "Emerging-markets equity",
    "FBTC": "Digital asset beta", "FBND": "Investment-grade bonds",
    "FIVA": "International value", "SGOV": "Treasury/cash",
    "TLT": "Long Treasury", "TIP": "Inflation-protected bonds",
    "Treasury bills": "Treasury/cash",
    "Treasury 10-year note": "Long Treasury",
    "Investment-grade bond fund": "Investment-grade bonds",
    "Global equity index fund": "International equity beta",
}

FUND_UNIVERSE = ("VOO", "VTI", "VNQ", "VWO", "FBTC", "FBND", "FIVA", "SGOV", "TLT", "TIP")
OPTIONAL_ASSETS: tuple[str, ...] = ()
# Explicit scenario inputs; Nasdaq Close/Last excludes fund distributions.
SCENARIO_EXPECTED_RETURNS = {
    "VOO": 0.08, "VTI": 0.08, "VNQ": 0.06, "VWO": 0.07, "FBTC": 0.12,
    "FBND": 0.045, "FIVA": 0.07, "SGOV": 0.035, "TLT": 0.045, "TIP": 0.04,
}
OVERLAP_NOTES = {
    "Treasury/cash": "Short Treasury exposure; the reserve candidate",
    "Long Treasury": "Long-duration Treasury exposure; not a cash reserve",
    "Investment-grade bonds": "Core bond exposure",
    "U.S. equity beta": "VOO and VTI substantially overlap",
    "International value": "Non-U.S. value tilt; check holdings overlap",
    "Emerging-markets equity": "Emerging-market equity exposure",
    "Real estate equity": "Listed real estate; may overlap broad U.S. equity funds",
    "Digital asset beta": "Single-asset bitcoin price exposure",
    "Inflation-protected bonds": "Treasury inflation-protected securities",
}

THEME_PORTFOLIOS = {
    "Core with reserve": ("VOO", "VTI", "VNQ", "VWO", "FBND", "SGOV"),
    "Fidelity blend": ("VTI", "VNQ", "FBTC", "FBND", "FIVA", "SGOV"),
    "Global value": ("VOO", "VWO", "FIVA", "FBND", "SGOV", "TIP"),
    "Real assets": ("VTI", "VNQ", "VWO", "FBTC", "SGOV", "TIP"),
    "Digital sleeve": ("VOO", "VTI", "FBTC", "FIVA", "FBND", "SGOV"),
    "Bond defense": ("VTI", "VNQ", "FBND", "SGOV", "TLT", "TIP"),
    "Treasury barbell": ("VOO", "VWO", "FBND", "SGOV", "TLT", "TIP"),
    "International tilt": ("VTI", "VWO", "FIVA", "FBND", "SGOV", "TIP"),
    "Equity conviction": ("VOO", "VTI", "VNQ", "VWO", "FBTC", "FIVA"),
    "Inflation watch": ("VTI", "VNQ", "VWO", "FBND", "SGOV", "TIP"),
}
THEME_DESCRIPTIONS = {
    "Core with reserve": "U.S. core, real estate, emerging markets, bonds, and bills.",
    "Fidelity blend": "Both selected Fidelity funds, bitcoin, and a short Treasury reserve.",
    "Global value": "Non-U.S. value and emerging markets beside bonds and TIPS.",
    "Real assets": "Real estate, bitcoin, and inflation protection with a bill reserve.",
    "Digital sleeve": "A bitcoin sleeve inside a broad equity and bond mix.",
    "Bond defense": "Bonds, bills, long Treasuries, and TIPS beside equities.",
    "Treasury barbell": "Short and long Treasury exposure with global equities.",
    "International tilt": "Emerging and non-U.S. value exposures together.",
    "Equity conviction": "Equity-heavy without an eligible reserve; it should fail that rule.",
    "Inflation watch": "Real estate and TIPS with bonds and bills.",
}


def validate_correlation(correlation: Iterable[Iterable[float]]) -> tuple[tuple[float, ...], ...]:
    """Return a checked square, symmetric correlation matrix."""
    matrix = tuple(tuple(float(value) for value in row) for row in correlation)
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("Correlation table must be square")
    tolerance = 1e-12
    for row in range(size):
        for column in range(size):
            value = matrix[row][column]
            if value < -1.0 - tolerance or value > 1.0 + tolerance:
                raise ValueError("Every correlation must be between -1 and 1")
            if not math.isclose(value, matrix[column][row], abs_tol=tolerance):
                raise ValueError("Correlation table must be symmetric")
        if not math.isclose(matrix[row][row], 1.0, abs_tol=tolerance):
            raise ValueError("Every diagonal correlation must equal 1")
    return tuple(
        tuple(1.0 if row == column else min(1.0, max(-1.0, matrix[row][column])) for column in range(size))
        for row in range(size)
    )


def covariance_matrix(
    volatilities: Iterable[float], correlation: Iterable[Iterable[float]]
) -> tuple[tuple[float, ...], ...]:
    """Build covariance as correlation multiplied by both asset volatilities."""
    volatility = tuple(float(value) for value in volatilities)
    if not volatility or any(value <= 0 or not math.isfinite(value) for value in volatility):
        raise ValueError("Every volatility must be positive and finite")
    matrix = validate_correlation(correlation)
    if len(matrix) != len(volatility):
        raise ValueError("Correlation dimensions must match the volatility inputs")
    return tuple(
        tuple(matrix[row][column] * volatility[row] * volatility[column] for column in range(len(volatility)))
        for row in range(len(volatility))
    )


def expected_portfolio_return(weights: Iterable[float], expected_returns: Iterable[float]) -> float:
    weights_tuple = tuple(float(value) for value in weights)
    returns_tuple = tuple(float(value) for value in expected_returns)
    if len(weights_tuple) != len(returns_tuple):
        raise ValueError("Weights and expected returns must have the same length")
    return sum(weight * expected for weight, expected in zip(weights_tuple, returns_tuple))


def portfolio_volatility(weights: Iterable[float], covariance: Iterable[Iterable[float]]) -> float:
    weights_tuple = tuple(float(value) for value in weights)
    matrix = tuple(tuple(float(value) for value in row) for row in covariance)
    if len(matrix) != len(weights_tuple) or any(len(row) != len(weights_tuple) for row in matrix):
        raise ValueError("Weights and covariance dimensions must match")
    variance = sum(
        weights_tuple[row] * weights_tuple[column] * matrix[row][column]
        for row in range(len(weights_tuple))
        for column in range(len(weights_tuple))
    )
    if variance < -1e-12:
        raise ValueError("Portfolio variance cannot be negative")
    return math.sqrt(max(variance, 0.0))


def _correlation_from_covariance(covariance: Iterable[Iterable[float]]) -> tuple[tuple[float, ...], ...]:
    """Recover correlations for constraint screens that receive covariance inputs."""
    matrix = tuple(tuple(float(value) for value in row) for row in covariance)
    if not matrix or any(len(row) != len(matrix) for row in matrix):
        raise ValueError("Covariance dimensions must be square")
    volatility = tuple(math.sqrt(matrix[index][index]) for index in range(len(matrix)))
    if any(value <= 0 or not math.isfinite(value) for value in volatility):
        raise ValueError("Covariance diagonal must be positive and finite")
    return tuple(
        tuple(matrix[row][column] / (volatility[row] * volatility[column]) for column in range(len(matrix)))
        for row in range(len(matrix))
    )


def reserve_weight(weights: Iterable[float], reserve_eligible: Iterable[bool]) -> float:
    weights_tuple = tuple(float(value) for value in weights)
    eligible_tuple = tuple(bool(value) for value in reserve_eligible)
    if len(weights_tuple) != len(eligible_tuple):
        raise ValueError("Weights and reserve flags must have the same length")
    return sum(max(weight, 0.0) for weight, eligible in zip(weights_tuple, eligible_tuple) if eligible)


def overlap_bucket_weights(
    weights: Iterable[float], groups: Iterable[str], gross: bool = False
) -> dict[str, float]:
    """Aggregate weights into broad exposure buckets as an overlap proxy."""
    weights_tuple = tuple(float(value) for value in weights)
    groups_tuple = tuple(str(group) for group in groups)
    if len(weights_tuple) != len(groups_tuple):
        raise ValueError("Weights and overlap groups must have the same length")
    totals: dict[str, float] = {}
    for weight, group in zip(weights_tuple, groups_tuple):
        contribution = abs(weight) if gross else weight
        totals[group] = totals.get(group, 0.0) + contribution
    return totals


def portfolio_max_drawdown(weights: Iterable[float], monthly_returns: dict[str, Iterable[float]]) -> float:
    """Return the historical peak-to-trough drawdown for a weighted monthly return path."""
    assets = tuple(monthly_returns)
    weights_tuple = tuple(float(value) for value in weights)
    series = tuple(tuple(float(value) for value in monthly_returns[asset]) for asset in assets)
    if len(weights_tuple) != len(series) or not series or len({len(values) for values in series}) != 1:
        raise ValueError("Weights and monthly return series must have matching dimensions")
    wealth = 1.0
    peak = 1.0
    worst_drawdown = 0.0
    for values in zip(*series):
        wealth *= 1.0 + sum(weight * value for weight, value in zip(weights_tuple, values))
        peak = max(peak, wealth)
        worst_drawdown = min(worst_drawdown, wealth / peak - 1.0)
    return -worst_drawdown


def overlap_groups_for_assets(assets: Iterable[str]) -> tuple[str, ...]:
    return tuple(OVERLAP_GROUPS.get(asset, asset) for asset in assets)


def available_assets(observed_assets: Iterable[str]) -> tuple[str, ...]:
    """Return the observed fund universe without fabricated price candidates."""
    return tuple(dict.fromkeys((*tuple(observed_assets), *OPTIONAL_ASSETS)))


def overlap_notes_for_groups(groups: Iterable[str]) -> tuple[str, ...]:
    return tuple(OVERLAP_NOTES.get(group, "Separate bucket; review holdings") for group in groups)


def pairwise_overlap_rows(
    weights: Iterable[float],
    assets: Iterable[str],
    correlation: Iterable[Iterable[float]],
    threshold: float = OVERLAP_CORRELATION_THRESHOLD,
) -> tuple[dict[str, object], ...]:
    """Report selected pairs whose estimated correlation indicates overlapping beta."""
    weights_tuple = tuple(float(value) for value in weights)
    assets_tuple = tuple(str(asset) for asset in assets)
    matrix = tuple(tuple(float(value) for value in row) for row in correlation)
    if len(weights_tuple) != len(assets_tuple) or len(matrix) != len(assets_tuple):
        raise ValueError("Weights, assets, and correlation dimensions must match")
    if any(len(row) != len(assets_tuple) for row in matrix):
        raise ValueError("Correlation dimensions must match the asset count")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Correlation threshold must be between 0 and 1")
    rows: list[dict[str, object]] = []
    for left in range(len(assets_tuple)):
        for right in range(left + 1, len(assets_tuple)):
            correlation_value = matrix[left][right]
            if correlation_value < threshold:
                continue
            left_weight = weights_tuple[left]
            right_weight = weights_tuple[right]
            if left_weight <= 1e-12 or right_weight <= 1e-12:
                continue
            rows.append(
                {
                    "Pair": f"{assets_tuple[left]} / {assets_tuple[right]}",
                    "Correlation": correlation_value,
                    "Combined weight": left_weight + right_weight,
                    "Left weight": left_weight,
                    "Right weight": right_weight,
                    "Reason": "High estimated correlation; combined weight is the screen",
                }
            )
    return tuple(sorted(rows, key=lambda row: (-float(row["Combined weight"]), str(row["Pair"]))))


def extend_estimate_with_candidates(estimate: dict[str, object]) -> dict[str, object]:
    """Preserve the observed universe; no unobserved funds are modeled in Project 2."""
    observed = tuple(str(asset) for asset in estimate["assets"])
    assets = available_assets(observed)
    expected_by_asset = dict(zip(observed, estimate["expected_returns"]))
    volatility_by_asset = dict(zip(observed, estimate["volatilities"]))
    observed_correlation = tuple(tuple(row) for row in estimate["correlations"])
    observed_index = {asset: index for index, asset in enumerate(observed)}
    expected = tuple(float(expected_by_asset[asset]) for asset in assets)
    volatility = tuple(float(volatility_by_asset[asset]) for asset in assets)

    def correlation_for(left: str, right: str) -> float:
        if left in observed_index and right in observed_index:
            return float(observed_correlation[observed_index[left]][observed_index[right]])
        if left == right:
            return 1.0
        raise ValueError(f"No observed correlation for {left} / {right}")

    correlation = tuple(
        tuple(correlation_for(left, right) for right in assets)
        for left in assets
    )
    return {
        **estimate,
        "assets": assets,
        "expected_returns": expected,
        "volatilities": volatility,
        "correlations": correlation,
        "observed_assets": observed,
        "modeled_assets": tuple(asset for asset in assets if asset not in observed),
    }


def equal_weight(asset_count: int) -> tuple[float, ...]:
    if asset_count <= 0:
        raise ValueError("Asset count must be positive")
    return tuple(1.0 / asset_count for _ in range(asset_count))


def inverse_volatility(volatilities: Iterable[float]) -> tuple[float, ...]:
    volatility = tuple(float(value) for value in volatilities)
    if not volatility or any(value <= 0 for value in volatility):
        raise ValueError("Every volatility must be positive")
    inverse = tuple(1.0 / value for value in volatility)
    scale = sum(inverse)
    return tuple(value / scale for value in inverse)


def portfolio_result(
    weights: Iterable[float],
    expected_returns: Iterable[float],
    covariance: Iterable[Iterable[float]],
    reserve_eligible: Iterable[bool],
) -> dict[str, object]:
    weights_tuple = tuple(float(value) for value in weights)
    return {
        "weights": weights_tuple,
        "expected_return": expected_portfolio_return(weights_tuple, expected_returns),
        "volatility": portfolio_volatility(weights_tuple, covariance),
        "reserve_weight": reserve_weight(weights_tuple, reserve_eligible),
    }


def _weight_units(asset_count: int, total_units: int) -> Iterable[tuple[int, ...]]:
    """Yield every nonnegative integer allocation whose units sum to the total."""
    if asset_count == 1:
        yield (total_units,)
        return
    for first in range(total_units + 1):
        for remainder in _weight_units(asset_count - 1, total_units - first):
            yield (first, *remainder)


def _bounded_weight_units(
    asset_count: int,
    total_units: int,
    minimum_units: int,
    maximum_units: int,
    gross_units: int,
) -> Iterable[tuple[int, ...]]:
    """Yield bounded net allocations with an optional gross-exposure ceiling."""
    if asset_count == 1:
        if minimum_units <= total_units <= maximum_units and abs(total_units) <= gross_units:
            yield (total_units,)
        return
    remaining_assets = asset_count - 1
    for first in range(minimum_units, maximum_units + 1):
        remaining_sum = total_units - first
        if remaining_sum < minimum_units * remaining_assets or remaining_sum > maximum_units * remaining_assets:
            continue
        remaining_gross = gross_units - abs(first)
        if remaining_gross < 0:
            continue
        for remainder in _bounded_weight_units(
            remaining_assets, remaining_sum, minimum_units, maximum_units, remaining_gross
        ):
            yield (first, *remainder)


def _allocation_units(
    asset_count: int,
    total_units: int,
    step: float,
    allow_shorting: bool,
    max_short_weight: float,
    max_asset_weight: float,
    max_gross_exposure: float,
) -> Iterable[tuple[int, ...]]:
    if not allow_shorting:
        yield from _weight_units(asset_count, total_units)
        return
    minimum_units = -round(max_short_weight / step)
    maximum_units = round(max_asset_weight / step)
    gross_units = round(max_gross_exposure / step)
    yield from _bounded_weight_units(
        asset_count, total_units, minimum_units, maximum_units, gross_units
    )


def search_lowest_risk_mix(
    expected_returns: Iterable[float],
    covariance: Iterable[Iterable[float]],
    objective: float,
    reserve_eligible: Iterable[bool],
    reserve_minimum: float,
    step: float = 0.05,
    overlap_groups: Iterable[str] | None = None,
    max_overlap_weight: float | None = None,
    max_asset_weight: float | None = None,
    max_pairwise_overlap_weight: float | None = None,
    correlation_threshold: float = OVERLAP_CORRELATION_THRESHOLD,
    allow_shorting: bool = False,
    max_short_weight: float = MAX_SHORT_WEIGHT,
    max_gross_exposure: float = MAX_GROSS_EXPOSURE,
    asset_caps: Iterable[float] | None = None,
) -> dict[str, object] | None:
    """Search bounded net allocations and return the lowest-volatility feasible mix."""
    expected = tuple(float(value) for value in expected_returns)
    eligible = tuple(bool(value) for value in reserve_eligible)
    groups = tuple(str(value) for value in overlap_groups) if overlap_groups is not None else None
    matrix = tuple(tuple(float(value) for value in row) for row in covariance)
    pairwise_correlation = _correlation_from_covariance(matrix)
    if len(expected) == 0 or len(eligible) != len(expected):
        raise ValueError("Expected returns and reserve flags must contain the same assets")
    if len(matrix) != len(expected) or any(len(row) != len(expected) for row in matrix):
        raise ValueError("Covariance dimensions must match the asset count")
    if not 0.0 < step <= 1.0 or not math.isclose(round(1.0 / step) * step, 1.0, abs_tol=1e-12):
        raise ValueError("Step must divide 100% exactly")
    if not 0.0 <= reserve_minimum <= 1.0:
        raise ValueError("Reserve minimum must be between 0% and 100%")
    if groups is not None and len(groups) != len(expected):
        raise ValueError("Overlap groups must match the asset count")
    if max_overlap_weight is not None and not 0.0 < max_overlap_weight <= 1.0:
        raise ValueError("Maximum overlap weight must be between 0% and 100%")
    if max_asset_weight is not None and not 0.0 < max_asset_weight <= 1.0:
        raise ValueError("Maximum asset weight must be between 0% and 100%")
    if max_pairwise_overlap_weight is not None and not 0.0 < max_pairwise_overlap_weight <= 1.0:
        raise ValueError("Maximum pairwise overlap weight must be between 0% and 100%")
    if not 0.0 <= correlation_threshold <= 1.0:
        raise ValueError("Correlation threshold must be between 0 and 1")
    if allow_shorting and not 0.0 < max_short_weight <= 1.0:
        raise ValueError("Maximum short weight must be between 0% and 100%")
    if not 1.0 <= max_gross_exposure <= 3.0:
        raise ValueError("Maximum gross exposure must be between 100% and 300%")
    effective_max_asset_weight = max_asset_weight if max_asset_weight is not None else 1.0
    caps = tuple(float(value) for value in asset_caps) if asset_caps is not None else (1.0,) * len(expected)
    if len(caps) != len(expected) or any(not 0 <= cap <= 1 for cap in caps):
        raise ValueError("Per-asset caps must align with the fund universe and be in [0, 1]")

    total_units = round(1.0 / step)
    best: dict[str, object] | None = None
    for units in _allocation_units(
        len(expected), total_units, step, allow_shorting, max_short_weight,
        effective_max_asset_weight, max_gross_exposure
    ):
        weights = tuple(value / total_units for value in units)
        result = portfolio_result(weights, expected, matrix, eligible)
        if result["expected_return"] + 1e-12 < objective:
            continue
        if result["reserve_weight"] + 1e-12 < reserve_minimum:
            continue
        if max_asset_weight is not None and max(weights) > max_asset_weight + 1e-12:
            continue
        if any(weight > cap + 1e-12 for weight, cap in zip(weights, caps)):
            continue
        if allow_shorting and min(weights) < -max_short_weight - 1e-12:
            continue
        if not allow_shorting and min(weights) < -1e-12:
            continue
        if sum(abs(weight) for weight in weights) > max_gross_exposure + 1e-12:
            continue
        if groups is not None and max_overlap_weight is not None:
            if max(overlap_bucket_weights(weights, groups, gross=True).values()) > max_overlap_weight + 1e-12:
                continue
        if max_pairwise_overlap_weight is not None:
            pair_rows = pairwise_overlap_rows(weights, range(len(expected)), pairwise_correlation, correlation_threshold)
            if any(float(row["Combined weight"]) > max_pairwise_overlap_weight + 1e-12 for row in pair_rows):
                continue
        if best is None or result["volatility"] < best["volatility"] - 1e-12:
            best = result
    return best


def risk_level_portfolios(
    expected_returns: Iterable[float],
    covariance: Iterable[Iterable[float]],
    objective: float,
    reserve_eligible: Iterable[bool],
    reserve_minimum: float,
    levels: int = 5,
    step: float = 0.05,
    overlap_groups: Iterable[str] | None = None,
    max_overlap_weight: float | None = None,
    max_asset_weight: float | None = None,
    max_pairwise_overlap_weight: float | None = None,
    correlation_threshold: float = OVERLAP_CORRELATION_THRESHOLD,
    allow_shorting: bool = False,
    max_short_weight: float = MAX_SHORT_WEIGHT,
    max_gross_exposure: float = MAX_GROSS_EXPOSURE,
    asset_caps: Iterable[float] | None = None,
) -> tuple[dict[str, object], ...]:
    """Return increasing-risk portfolios sampled from the feasible efficient frontier."""
    expected = tuple(float(value) for value in expected_returns)
    eligible = tuple(bool(value) for value in reserve_eligible)
    groups = tuple(str(value) for value in overlap_groups) if overlap_groups is not None else None
    matrix = tuple(tuple(float(value) for value in row) for row in covariance)
    pairwise_correlation = _correlation_from_covariance(matrix)
    if len(expected) == 0 or len(eligible) != len(expected):
        raise ValueError("Expected returns and reserve flags must contain the same assets")
    if len(matrix) != len(expected) or any(len(row) != len(expected) for row in matrix):
        raise ValueError("Covariance dimensions must match the asset count")
    if not 0.0 < step <= 1.0 or not math.isclose(round(1.0 / step) * step, 1.0, abs_tol=1e-12):
        raise ValueError("Step must divide 100% exactly")
    if not 0.0 <= reserve_minimum <= 1.0:
        raise ValueError("Reserve minimum must be between 0% and 100%")
    if groups is not None and len(groups) != len(expected):
        raise ValueError("Overlap groups must match the asset count")
    if max_overlap_weight is not None and not 0.0 < max_overlap_weight <= 1.0:
        raise ValueError("Maximum overlap weight must be between 0% and 100%")
    if max_asset_weight is not None and not 0.0 < max_asset_weight <= 1.0:
        raise ValueError("Maximum asset weight must be between 0% and 100%")
    if max_pairwise_overlap_weight is not None and not 0.0 < max_pairwise_overlap_weight <= 1.0:
        raise ValueError("Maximum pairwise overlap weight must be between 0% and 100%")
    if not 0.0 <= correlation_threshold <= 1.0:
        raise ValueError("Correlation threshold must be between 0 and 1")
    if allow_shorting and not 0.0 < max_short_weight <= 1.0:
        raise ValueError("Maximum short weight must be between 0% and 100%")
    if not 1.0 <= max_gross_exposure <= 3.0:
        raise ValueError("Maximum gross exposure must be between 100% and 300%")
    effective_max_asset_weight = max_asset_weight if max_asset_weight is not None else 1.0
    caps = tuple(float(value) for value in asset_caps) if asset_caps is not None else (1.0,) * len(expected)
    if len(caps) != len(expected) or any(not 0 <= cap <= 1 for cap in caps):
        raise ValueError("Per-asset caps must align with the fund universe and be in [0, 1]")
    if levels <= 0:
        raise ValueError("Levels must be positive")

    total_units = round(1.0 / step)
    feasible: list[dict[str, object]] = []
    for units in _allocation_units(
        len(expected), total_units, step, allow_shorting, max_short_weight,
        effective_max_asset_weight, max_gross_exposure
    ):
        weights = tuple(value / total_units for value in units)
        result = portfolio_result(weights, expected, matrix, eligible)
        if result["expected_return"] + 1e-12 < objective:
            continue
        if result["reserve_weight"] + 1e-12 < reserve_minimum:
            continue
        if max_asset_weight is not None and max(weights) > max_asset_weight + 1e-12:
            continue
        if any(weight > cap + 1e-12 for weight, cap in zip(weights, caps)):
            continue
        if allow_shorting and min(weights) < -max_short_weight - 1e-12:
            continue
        if not allow_shorting and min(weights) < -1e-12:
            continue
        if sum(abs(weight) for weight in weights) > max_gross_exposure + 1e-12:
            continue
        if groups is not None and max_overlap_weight is not None:
            if max(overlap_bucket_weights(weights, groups, gross=True).values()) > max_overlap_weight + 1e-12:
                continue
        if max_pairwise_overlap_weight is not None:
            pair_rows = pairwise_overlap_rows(weights, range(len(expected)), pairwise_correlation, correlation_threshold)
            if any(float(row["Combined weight"]) > max_pairwise_overlap_weight + 1e-12 for row in pair_rows):
                continue
        feasible.append(result)

    if not feasible:
        return ()

    feasible.sort(key=lambda result: (result["volatility"], -result["expected_return"]))
    frontier: list[dict[str, object]] = []
    best_return = -math.inf
    for result in feasible:
        if result["expected_return"] > best_return + 1e-12:
            frontier.append(result)
            best_return = result["expected_return"]

    if levels == 1:
        return (frontier[0],)
    if len(frontier) <= levels:
        return tuple(frontier)
    indices = [round(index * (len(frontier) - 1) / (levels - 1)) for index in range(levels)]
    return tuple(frontier[index] for index in indices)


def audit_theme_portfolios(
    themes: Iterable[tuple[str, Iterable[str]]],
    assets: Iterable[str],
    expected_returns: Iterable[float],
    volatilities: Iterable[float],
    correlation: Iterable[Iterable[float]],
    objective: float,
    reserve_minimum: float,
    max_overlap_weight: float,
    max_asset_weight: float,
    max_pairwise_overlap_weight: float,
    correlation_threshold: float,
    allow_shorting: bool = False,
    max_short_weight: float = MAX_SHORT_WEIGHT,
    max_gross_exposure: float = MAX_GROSS_EXPOSURE,
    step: float = 0.05,
    max_bitcoin_weight: float = MAX_BITCOIN_WEIGHT,
) -> tuple[dict[str, object], ...]:
    """Run the same constrained search across each named six-fund starting theme."""
    all_assets = tuple(str(asset) for asset in assets)
    expected_by_asset = dict(zip(all_assets, expected_returns))
    volatility_by_asset = dict(zip(all_assets, volatilities))
    matrix = tuple(tuple(float(value) for value in row) for row in correlation)
    asset_index = {asset: index for index, asset in enumerate(all_assets)}
    rows: list[dict[str, object]] = []
    for name, theme_assets in themes:
        theme = tuple(str(asset) for asset in theme_assets)
        if any(asset not in asset_index for asset in theme):
            rows.append({"Theme": name, "Assets": ", ".join(theme), "Result": None, "Reason": "Ticker unavailable"})
            continue
        indices = [asset_index[asset] for asset in theme]
        theme_expected = tuple(float(expected_by_asset[asset]) for asset in theme)
        theme_volatility = tuple(float(volatility_by_asset[asset]) for asset in theme)
        theme_correlation = tuple(
            tuple(matrix[row][column] for column in indices) for row in indices
        )
        reserve_flags = tuple(asset == "SGOV" for asset in theme)
        result = search_lowest_risk_mix(
            theme_expected,
            covariance_matrix(theme_volatility, theme_correlation),
            objective,
            reserve_flags,
            reserve_minimum,
            step=step,
            overlap_groups=overlap_groups_for_assets(theme),
            max_overlap_weight=max_overlap_weight,
            max_asset_weight=max_asset_weight,
            max_pairwise_overlap_weight=max_pairwise_overlap_weight,
            correlation_threshold=correlation_threshold,
            allow_shorting=allow_shorting,
            max_short_weight=max_short_weight,
            max_gross_exposure=max_gross_exposure,
            asset_caps=tuple(max_bitcoin_weight if asset == "FBTC" else 1.0 for asset in theme),
        )
        rows.append(
            {
                "Theme": name,
                "Assets": ", ".join(theme),
                "Result": result,
                "Reason": "Feasible under allocation controls" if result else "No feasible mix under allocation controls",
            }
        )
    return tuple(rows)


def _read_csv_text(source: str | Path | TextIO | BinaryIO) -> str:
    if isinstance(source, (str, Path)):
        return Path(source).read_text(encoding="utf-8-sig")
    position = source.tell() if hasattr(source, "tell") else None
    raw = source.read()
    if position is not None and hasattr(source, "seek"):
        source.seek(position)
    return raw.decode("utf-8-sig") if isinstance(raw, bytes) else str(raw)


def _sample_correlation(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("Correlation requires equal series with at least two returns")
    left_mean = mean(left)
    right_mean = mean(right)
    covariance = sum(
        (left_value - left_mean) * (right_value - right_mean)
        for left_value, right_value in zip(left, right)
    ) / (len(left) - 1)
    denominator = stdev(left) * stdev(right)
    if denominator == 0:
        raise ValueError("Correlation is undefined for a zero-volatility asset")
    return covariance / denominator


def estimate_from_prices(
    source: str | Path | TextIO | BinaryIO,
    last_36: bool = False,
    return_window: int | None = None,
) -> dict[str, object]:
    """Estimate price-change return, volatility and correlation from monthly closes."""
    if last_36 and return_window is not None:
        raise ValueError("Choose either last_36 or return_window, not both")
    if return_window is not None and return_window < 2:
        raise ValueError("Return window must contain at least two monthly returns")
    reader = csv.DictReader(io.StringIO(_read_csv_text(source)))
    if not reader.fieldnames or len(reader.fieldnames) < 2:
        raise ValueError("CSV must contain a date column followed by one or more ticker columns")
    date_column = reader.fieldnames[0]
    assets = tuple(reader.fieldnames[1:])
    dates: list[str] = []
    prices = {asset: [] for asset in assets}
    for row_number, row in enumerate(reader, start=2):
        date = (row.get(date_column) or "").strip()
        if not date:
            raise ValueError(f"Missing date on CSV row {row_number}")
        if dates and date <= dates[-1]:
            raise ValueError("Dates must be unique and ordered from oldest to newest")
        dates.append(date)
        for asset in assets:
            try:
                value = float(row[asset])
            except (TypeError, ValueError) as error:
                raise ValueError(f"{asset}: invalid price on CSV row {row_number}") from error
            if value <= 0 or not math.isfinite(value):
                raise ValueError(f"{asset}: prices must be positive and finite")
            prices[asset].append(value)

    if len(dates) < 3:
        raise ValueError("CSV must contain at least three monthly price observations")
    returns = {
        asset: [current / previous - 1.0 for previous, current in zip(values, values[1:])]
        for asset, values in prices.items()
    }
    selected_window = 36 if last_36 else return_window
    if selected_window is not None:
        if len(dates) <= selected_window:
            raise ValueError(f"At least {selected_window + 1} prices are required for {selected_window} monthly returns")
        returns = {asset: values[-selected_window:] for asset, values in returns.items()}
        estimate_start = dates[-selected_window - 1]
    else:
        estimate_start = dates[0]

    observations = len(next(iter(returns.values())))
    expected = tuple(mean(returns[asset]) * 12.0 for asset in assets)
    volatility = tuple(stdev(returns[asset]) * math.sqrt(12.0) for asset in assets)
    correlation = tuple(
        tuple(_sample_correlation(returns[left], returns[right]) for right in assets)
        for left in assets
    )
    validate_correlation(correlation)
    return {
        "assets": assets,
        "expected_returns": expected,
        "volatilities": volatility,
        "correlations": correlation,
        "return_observations": observations,
        "start_date": estimate_start,
        "end_date": dates[-1],
        "monthly_returns": returns,
    }


def meridian_covariance() -> tuple[tuple[float, ...], ...]:
    return covariance_matrix(VOLATILITIES, CORRELATIONS)


def meridian_baselines() -> tuple[tuple[str, dict[str, object]], ...]:
    covariance = meridian_covariance()
    portfolios = (
        ("Benchmark", (0.0, 0.0, 0.4, 0.6)),
        ("Equal weight", equal_weight(len(ASSETS))),
        ("Inverse volatility", inverse_volatility(VOLATILITIES)),
    )
    return tuple(
        (name, portfolio_result(weights, EXPECTED_RETURNS, covariance, RESERVE_ELIGIBLE))
        for name, weights in portfolios
    )


def _validate_lab_answers() -> None:
    covariance = meridian_covariance()
    baselines = dict(meridian_baselines())
    expected_baselines = {
        "Benchmark": ((0.0, 0.0, 0.4, 0.6), 0.0680, 0.1046, 0.0),
        "Equal weight": ((0.25, 0.25, 0.25, 0.25), 0.0520, 0.0521, 0.5),
        "Inverse volatility": ((0.843, 0.060, 0.070, 0.026), 0.0377, 0.0105, 0.903),
    }
    for name, (weights, expected_return, volatility, reserve) in expected_baselines.items():
        result = baselines[name]
        if any(abs(actual - target) > 0.0006 for actual, target in zip(result["weights"], weights)):
            raise AssertionError(f"{name} weights do not match the Lab 14 known answer")
        if abs(result["expected_return"] - expected_return) > 0.00006:
            raise AssertionError(f"{name} return does not match the Lab 14 known answer")
        if abs(result["volatility"] - volatility) > 0.00006:
            raise AssertionError(f"{name} volatility does not match the Lab 14 known answer")
        if abs(result["reserve_weight"] - reserve) > 0.0006:
            raise AssertionError(f"{name} reserve does not match the Lab 14 known answer")

    loaded = search_lowest_risk_mix(
        EXPECTED_RETURNS, covariance, CLASSROOM_OBJECTIVE_RETURN, RESERVE_ELIGIBLE, CLASSROOM_RESERVE_MINIMUM
    )
    stressed_returns = (*EXPECTED_RETURNS[:-1], 0.070)
    stressed = search_lowest_risk_mix(
        stressed_returns, covariance, CLASSROOM_OBJECTIVE_RETURN, RESERVE_ELIGIBLE, CLASSROOM_RESERVE_MINIMUM
    )
    if loaded is None or stressed is None:
        raise AssertionError("Lab 15 known-answer search unexpectedly returned no mix")
    if loaded["weights"] != (0.0, 0.20, 0.25, 0.55):
        raise AssertionError("Loaded Lab 15 weights do not match the known answer")
    if stressed["weights"] != (0.0, 0.10, 0.10, 0.80):
        raise AssertionError("Stressed Lab 15 weights do not match the known answer")


def print_meridian_baselines() -> None:
    print("MERIDIAN PORTFOLIO BASELINES")
    print(f"Objective return: {CLASSROOM_OBJECTIVE_RETURN:.1%}")
    for name, result in meridian_baselines():
        weights = " / ".join(f"{weight:.1%}" for weight in result["weights"])
        meets = "yes" if result["expected_return"] >= CLASSROOM_OBJECTIVE_RETURN else "no"
        print(f"\n{name}")
        print(f"Weights (bills / 10-year / IG / equity): {weights}")
        print(f"Expected return: {result['expected_return']:.2%}")
        print(f"Volatility: {result['volatility']:.2%}")
        print(f"Reserve-eligible weight: {result['reserve_weight']:.1%}")
        print(f"Meets {CLASSROOM_OBJECTIVE_RETURN:.1%} objective: {meets}")


if __name__ == "__main__":
    _validate_lab_answers()
    print_meridian_baselines()



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.

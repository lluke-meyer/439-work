"""FIN 439 Lab 15 portfolio engine and price-history estimates."""

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
OBJECTIVE_RETURN = 0.065
RESERVE_ELIGIBLE = (True, True, False, False)
RESERVE_MINIMUM = 0.03


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


def reserve_weight(weights: Iterable[float], reserve_eligible: Iterable[bool]) -> float:
    weights_tuple = tuple(float(value) for value in weights)
    eligible_tuple = tuple(bool(value) for value in reserve_eligible)
    if len(weights_tuple) != len(eligible_tuple):
        raise ValueError("Weights and reserve flags must have the same length")
    return sum(weight for weight, eligible in zip(weights_tuple, eligible_tuple) if eligible)


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


def search_lowest_risk_mix(
    expected_returns: Iterable[float],
    covariance: Iterable[Iterable[float]],
    objective: float,
    reserve_eligible: Iterable[bool],
    reserve_minimum: float,
    step: float = 0.05,
) -> dict[str, object] | None:
    """Search every long-only allocation on a fixed grid and return the lowest-volatility feasible mix."""
    expected = tuple(float(value) for value in expected_returns)
    eligible = tuple(bool(value) for value in reserve_eligible)
    matrix = tuple(tuple(float(value) for value in row) for row in covariance)
    if len(expected) == 0 or len(eligible) != len(expected):
        raise ValueError("Expected returns and reserve flags must contain the same assets")
    if len(matrix) != len(expected) or any(len(row) != len(expected) for row in matrix):
        raise ValueError("Covariance dimensions must match the asset count")
    if not 0.0 < step <= 1.0 or not math.isclose(round(1.0 / step) * step, 1.0, abs_tol=1e-12):
        raise ValueError("Step must divide 100% exactly")
    if not 0.0 <= reserve_minimum <= 1.0:
        raise ValueError("Reserve minimum must be between 0% and 100%")

    total_units = round(1.0 / step)
    best: dict[str, object] | None = None
    for units in _weight_units(len(expected), total_units):
        weights = tuple(value / total_units for value in units)
        result = portfolio_result(weights, expected, matrix, eligible)
        if result["expected_return"] + 1e-12 < objective:
            continue
        if result["reserve_weight"] + 1e-12 < reserve_minimum:
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
) -> tuple[dict[str, object], ...]:
    """Return increasing-risk portfolios sampled from the feasible efficient frontier."""
    expected = tuple(float(value) for value in expected_returns)
    eligible = tuple(bool(value) for value in reserve_eligible)
    matrix = tuple(tuple(float(value) for value in row) for row in covariance)
    if len(expected) == 0 or len(eligible) != len(expected):
        raise ValueError("Expected returns and reserve flags must contain the same assets")
    if len(matrix) != len(expected) or any(len(row) != len(expected) for row in matrix):
        raise ValueError("Covariance dimensions must match the asset count")
    if not 0.0 < step <= 1.0 or not math.isclose(round(1.0 / step) * step, 1.0, abs_tol=1e-12):
        raise ValueError("Step must divide 100% exactly")
    if not 0.0 <= reserve_minimum <= 1.0:
        raise ValueError("Reserve minimum must be between 0% and 100%")
    if levels <= 0:
        raise ValueError("Levels must be positive")

    total_units = round(1.0 / step)
    feasible: list[dict[str, object]] = []
    for units in _weight_units(len(expected), total_units):
        weights = tuple(value / total_units for value in units)
        result = portfolio_result(weights, expected, matrix, eligible)
        if result["expected_return"] + 1e-12 < objective:
            continue
        if result["reserve_weight"] + 1e-12 < reserve_minimum:
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
    source: str | Path | TextIO | BinaryIO, last_36: bool = False
) -> dict[str, object]:
    """Estimate annual return, volatility and correlation from monthly adjusted-close prices."""
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
    if last_36:
        if len(dates) < 37:
            raise ValueError("At least 37 prices are required for 36 monthly returns")
        returns = {asset: values[-36:] for asset, values in returns.items()}
        estimate_start = dates[-37]
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
        EXPECTED_RETURNS, covariance, OBJECTIVE_RETURN, RESERVE_ELIGIBLE, RESERVE_MINIMUM
    )
    stressed_returns = (*EXPECTED_RETURNS[:-1], 0.070)
    stressed = search_lowest_risk_mix(
        stressed_returns, covariance, OBJECTIVE_RETURN, RESERVE_ELIGIBLE, RESERVE_MINIMUM
    )
    if loaded is None or stressed is None:
        raise AssertionError("Lab 15 known-answer search unexpectedly returned no mix")
    if loaded["weights"] != (0.0, 0.20, 0.25, 0.55):
        raise AssertionError("Loaded Lab 15 weights do not match the known answer")
    if stressed["weights"] != (0.0, 0.10, 0.10, 0.80):
        raise AssertionError("Stressed Lab 15 weights do not match the known answer")


def print_meridian_baselines() -> None:
    print("MERIDIAN PORTFOLIO BASELINES")
    print(f"Objective return: {OBJECTIVE_RETURN:.1%}")
    for name, result in meridian_baselines():
        weights = " / ".join(f"{weight:.1%}" for weight in result["weights"])
        meets = "yes" if result["expected_return"] >= OBJECTIVE_RETURN else "no"
        print(f"\n{name}")
        print(f"Weights (bills / 10-year / IG / equity): {weights}")
        print(f"Expected return: {result['expected_return']:.2%}")
        print(f"Volatility: {result['volatility']:.2%}")
        print(f"Reserve-eligible weight: {result['reserve_weight']:.1%}")
        print(f"Meets {OBJECTIVE_RETURN:.1%} objective: {meets}")


if __name__ == "__main__":
    _validate_lab_answers()
    print_meridian_baselines()

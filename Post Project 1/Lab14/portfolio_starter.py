"""Lab 14 portfolio baselines, mechanics-only candidate, and validation checks."""

from __future__ import annotations

from itertools import combinations
import json
from pathlib import Path

import numpy as np
import pandas as pd


def load_inputs(folder: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    folder = Path(folder)
    stats = pd.read_csv(folder / "asset_statistics.csv")
    corr = pd.read_csv(folder / "correlation.csv", index_col="asset")
    assets = list(stats["asset"])
    if list(corr.index) != assets or list(corr.columns) != assets:
        raise ValueError("Correlation matrix labels/order must match statistics")
    if not np.allclose(corr, corr.T) or not np.allclose(np.diag(corr), 1.0):
        raise ValueError("Correlation matrix must be symmetric with a unit diagonal")
    if not np.isfinite(stats[["expected_return", "volatility"]].to_numpy()).all():
        raise ValueError("Return and volatility inputs must be finite")
    if (stats["volatility"] <= 0).any():
        raise ValueError("Volatility inputs must be positive")
    return stats, corr


def equal_weight(n_assets: int) -> np.ndarray:
    if n_assets <= 0:
        raise ValueError("n_assets must be positive")
    return np.repeat(1.0 / n_assets, n_assets)


def inverse_volatility(stats: pd.DataFrame) -> np.ndarray:
    """Return normalized inverse-volatility weights."""
    volatility = stats["volatility"].to_numpy(dtype=float)
    if np.any(volatility <= 0):
        raise ValueError("Volatility inputs must be positive")
    inverse = 1.0 / volatility
    return inverse / inverse.sum()


def covariance_matrix(stats: pd.DataFrame, corr: pd.DataFrame) -> np.ndarray:
    """Construct annualized covariance from annualized volatility and correlation."""
    volatility = stats["volatility"].to_numpy(dtype=float)
    correlation = corr.to_numpy(dtype=float)
    covariance = np.diag(volatility) @ correlation @ np.diag(volatility)
    return covariance


def constrained_allocation(stats: pd.DataFrame, covariance: np.ndarray, mandate: dict) -> np.ndarray:
    """Compute the long-only global minimum-variance mechanics candidate.

    The CIO objective remains unresolved. This active-set enumeration solves only the stated
    classroom objective: minimize annualized variance subject to weights summing to one and no
    negative weights. It does not establish issuer, liquidity, turnover, cost, or loss-rule
    compliance because the supplied inputs do not contain the evidence those checks require.
    """
    objective = str(mandate.get("objective", "")).lower()
    if "unresolved" not in objective or "mechanics-only" not in objective:
        raise ValueError("Mandate must preserve the unresolved objective and mechanics-only boundary")

    n_assets = len(stats)
    if covariance.shape != (n_assets, n_assets):
        raise ValueError("Covariance dimensions must match the asset count")

    best_variance = np.inf
    best_weights: np.ndarray | None = None
    tolerance = 1e-12

    # A long-only optimum lies on one of the nonempty asset subsets. For each subset, solve the
    # equality-constrained minimum-variance portfolio and retain only nonnegative candidates.
    for subset_size in range(1, n_assets + 1):
        for subset in combinations(range(n_assets), subset_size):
            subset_covariance = covariance[np.ix_(subset, subset)]
            ones = np.ones(subset_size)
            try:
                raw = np.linalg.solve(subset_covariance, ones)
            except np.linalg.LinAlgError:
                continue
            denominator = float(ones @ raw)
            if denominator <= 0:
                continue
            subset_weights = raw / denominator
            if np.min(subset_weights) < -tolerance:
                continue

            weights = np.zeros(n_assets)
            weights[list(subset)] = np.clip(subset_weights, 0.0, None)
            weights /= weights.sum()
            variance = float(weights @ covariance @ weights)
            if variance < best_variance:
                best_variance = variance
                best_weights = weights

    if best_weights is None:
        raise ValueError("No feasible long-only allocation was found")
    return best_weights


def portfolio_metrics(
    stats: pd.DataFrame, covariance: np.ndarray, weights: np.ndarray
) -> tuple[float, float]:
    """Return annualized expected return and volatility."""
    expected_return = float(weights @ stats["expected_return"].to_numpy(dtype=float))
    variance = float(weights @ covariance @ weights)
    return expected_return, float(np.sqrt(max(variance, 0.0)))


def mechanical_checks(
    stats: pd.DataFrame,
    corr: pd.DataFrame,
    covariance: np.ndarray,
    weights: np.ndarray,
) -> dict[str, str]:
    """Return reproducible checks supported by the supplied tables."""
    eigenvalues = np.linalg.eigvalsh(covariance)
    volatility = stats["volatility"].to_numpy(dtype=float)
    return {
        "Correlation labels/order": "PASS",
        "Correlation symmetry": "PASS" if np.allclose(corr, corr.T) else "FAIL",
        "Correlation unit diagonal": "PASS" if np.allclose(np.diag(corr), 1.0) else "FAIL",
        "Covariance diagonal": "PASS" if np.allclose(np.diag(covariance), volatility**2) else "FAIL",
        "Covariance positive semidefinite": "PASS" if eigenvalues.min() >= -1e-12 else "FAIL",
        "Weights sum to one": "PASS" if abs(float(weights.sum()) - 1.0) <= 1e-10 else "FAIL",
        "Long-only": "PASS" if weights.min() >= -1e-12 else "FAIL",
        "No leverage": "PASS" if float(np.abs(weights).sum()) <= 1.0 + 1e-10 else "FAIL",
        "Finite outputs": "PASS" if np.isfinite(weights).all() else "FAIL",
    }


def comparison_table(
    stats: pd.DataFrame, covariance: np.ndarray, mandate: dict
) -> pd.DataFrame:
    """Build the required baseline and candidate comparison."""
    portfolios = {
        "Equal weight": equal_weight(len(stats)),
        "Inverse volatility": inverse_volatility(stats),
        "Mechanics candidate": constrained_allocation(stats, covariance, mandate),
    }
    rows = []
    for name, weights in portfolios.items():
        expected_return, volatility = portfolio_metrics(stats, covariance, weights)
        row = {"portfolio": name}
        row.update(dict(zip(stats["asset"], weights)))
        row.update({"expected_return": expected_return, "volatility": volatility})
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    folder = Path(__file__).parent
    stats, corr = load_inputs(folder)
    with (folder.parent / "Lab13" / "mandate.json").open(encoding="utf-8") as stream:
        mandate = json.load(stream)

    covariance = covariance_matrix(stats, corr)
    comparison = comparison_table(stats, covariance, mandate)
    candidate = comparison.loc[comparison["portfolio"] == "Mechanics candidate"].iloc[0]
    candidate_weights = candidate[stats["asset"].tolist()].to_numpy(dtype=float)
    checks = mechanical_checks(stats, corr, covariance, candidate_weights)

    # Retain the course known answers and validation gates inside the runnable model.
    if not np.isclose(covariance[0, 0], 0.003600):
        raise AssertionError("GovBond variance known answer failed")
    if not np.isclose(covariance[2, 3], 0.027000):
        raise AssertionError("Equity covariance known answer failed")
    failed_checks = [name for name, result in checks.items() if result != "PASS"]
    if failed_checks:
        raise AssertionError(f"Mechanical checks failed: {failed_checks}")

    print("LAB 14 — PORTFOLIO CONSTRUCTION AND STABILITY")
    print("Evidence vintage: Oct. 20, 2026 course release")
    print("Decision: DEFERRED_NO_ADOPTABLE_CANDIDATE")
    print("Classroom objective: long-only global minimum variance; mechanics only")
    print("\nINPUTS")
    print(stats.to_string(index=False))
    print("\nCOVARIANCE MATRIX")
    covariance_display = pd.DataFrame(
        covariance,
        index=stats["asset"].tolist(),
        columns=stats["asset"].tolist(),
    )
    print(covariance_display.to_string())
    print("\nBASELINES AND CANDIDATE")
    print(comparison.to_string(index=False, float_format=lambda value: f"{value:.6f}"))
    print("\nMECHANICAL CHECKS")
    for check, result in checks.items():
        print(f"{check}: {result}")
    print("\nUNAVAILABLE FROM SUPPLIED TABLES")
    print("Issuer cap, eligible $3m liquidity reserve, five-day liquidity, turnover, costs, and 10% loss rule")
    print("\nFINAL STATUS")
    print("Candidate calculated for mechanics practice only; committee adoption remains deferred.")

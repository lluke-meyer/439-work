import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from backtest import run_backtest  # noqa: E402
from portfolio import (  # noqa: E402
    available_assets,
    covariance_matrix,
    estimate_from_prices,
    extend_estimate_with_candidates,
    overlap_bucket_weights,
    overlap_groups_for_assets,
    pairwise_overlap_rows,
    search_lowest_risk_mix,
)


class Project2ModelTests(unittest.TestCase):
    def test_frozen_backtest_matches_lab_known_answer(self):
        result = run_backtest()
        self.assertAlmostEqual(result["development"]["net"], 0.0612989205, places=8)
        self.assertAlmostEqual(result["holdout"]["net"], -0.0609153714, places=8)
        self.assertTrue(result["failure_triggered"])

    def test_zero_lag_is_rejected_as_a_leakage_diagnostic(self):
        result = run_backtest(lag_months=0)
        self.assertAlmostEqual(result["development"]["net"], 0.1772, places=4)
        self.assertGreater(result["development"]["net"], run_backtest()["development"]["net"])

    def test_constrained_search_meets_current_classroom_controls(self):
        estimate = estimate_from_prices(PROJECT_DIR / "prices.csv")
        covariance = covariance_matrix(estimate["volatilities"], estimate["correlations"])
        reserve_flags = tuple(asset == "TLT" for asset in estimate["assets"])
        result = search_lowest_risk_mix(
            estimate["expected_returns"], covariance, 0.065, reserve_flags, 0.03
        )
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result["expected_return"], 0.065)
        self.assertGreaterEqual(result["reserve_weight"], 0.03)

    def test_final_gate_requires_reserve_and_limits_overlap(self):
        estimate = estimate_from_prices(PROJECT_DIR / "prices.csv")
        covariance = covariance_matrix(estimate["volatilities"], estimate["correlations"])
        groups = overlap_groups_for_assets(estimate["assets"])
        no_reserve = search_lowest_risk_mix(
            estimate["expected_returns"], covariance, 0.09,
            (False,) * len(estimate["assets"]), 0.01,
            overlap_groups=groups, max_overlap_weight=0.60, max_asset_weight=0.40,
        )
        self.assertIsNone(no_reserve)
        with_tlt_proxy = search_lowest_risk_mix(
            estimate["expected_returns"], covariance, 0.09,
            (True,) + (False,) * (len(estimate["assets"]) - 1), 0.01,
            overlap_groups=groups, max_overlap_weight=0.60, max_asset_weight=0.40,
        )
        self.assertIsNotNone(with_tlt_proxy)
        self.assertLessEqual(max(with_tlt_proxy["weights"]), 0.40)
        self.assertLessEqual(max(overlap_bucket_weights(with_tlt_proxy["weights"], groups).values()), 0.60)

    def test_optional_candidates_and_pairwise_overlap_screen(self):
        estimate = extend_estimate_with_candidates(estimate_from_prices(PROJECT_DIR / "prices.csv"))
        self.assertEqual(available_assets(("TLT", "VTI"))[-4:], ("SGOV", "BND", "VOO", "TIP"))
        self.assertEqual(estimate["modeled_assets"], ("SGOV", "BND", "VOO", "TIP"))
        rows = pairwise_overlap_rows(
            (0.40, 0.30, 0.20),
            ("VTI", "VOO", "SGOV"),
            ((1.0, 0.95, 0.0), (0.95, 1.0, 0.0), (0.0, 0.0, 1.0)),
        )
        self.assertEqual(rows[0]["Pair"], "VTI / VOO")
        self.assertAlmostEqual(rows[0]["Combined weight"], 0.70)

    def test_bounded_short_and_gross_exposure_constraints(self):
        estimate = estimate_from_prices(PROJECT_DIR / "prices.csv")
        covariance = covariance_matrix(estimate["volatilities"], estimate["correlations"])
        result = search_lowest_risk_mix(
            estimate["expected_returns"], covariance, 0.065,
            (True,) + (False,) * (len(estimate["assets"]) - 1), 0.03,
            step=0.10,
            allow_shorting=True,
            max_short_weight=0.10,
            max_gross_exposure=1.10,
            max_asset_weight=0.40,
        )
        self.assertIsNotNone(result)
        self.assertGreaterEqual(min(result["weights"]), -0.10)
        self.assertLessEqual(sum(abs(weight) for weight in result["weights"]), 1.10)


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from backtest import run_backtest  # noqa: E402
from auto_pass import best_numerical_mix, usable_return_target  # noqa: E402
from mandate_finder import mandate_boundaries, numerical_mandate_pass  # noqa: E402
from process_audit import full_process_pass_report  # noqa: E402
from portfolio import (  # noqa: E402
    FUND_UNIVERSE,
    SCENARIO_EXPECTED_RETURNS,
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

    def test_constrained_search_meets_six_fund_scenario_controls(self):
        estimate = estimate_from_prices(PROJECT_DIR / "prices.csv")
        self.assertEqual(estimate["assets"], FUND_UNIVERSE)
        self.assertEqual(estimate["return_observations"], 32)
        selected = ("VOO", "VTI", "VNQ", "VWO", "FBND", "SGOV")
        indices = [estimate["assets"].index(asset) for asset in selected]
        covariance = covariance_matrix(
            (estimate["volatilities"][index] for index in indices),
            ((estimate["correlations"][left][right] for right in indices) for left in indices),
        )
        reserve_flags = tuple(asset == "SGOV" for asset in selected)
        result = search_lowest_risk_mix(
            (0.08, 0.08, 0.06, 0.07, 0.045, 0.035), covariance,
            0.065, reserve_flags, 0.03, step=0.10,
        )
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result["expected_return"], 0.065)
        self.assertGreaterEqual(result["reserve_weight"], 0.03)

    def test_bundled_estimation_window_changes_risk_sample(self):
        full = estimate_from_prices(PROJECT_DIR / "prices.csv")
        recent = estimate_from_prices(PROJECT_DIR / "prices.csv", return_window=24)
        self.assertEqual(full["return_observations"], 32)
        self.assertEqual(recent["return_observations"], 24)
        self.assertEqual(recent["start_date"], "2024-09-30")
        self.assertNotEqual(full["volatilities"], recent["volatilities"])
        self.assertNotEqual(full["correlations"], recent["correlations"])
        with self.assertRaisesRegex(ValueError, "At least 37 prices"):
            estimate_from_prices(PROJECT_DIR / "prices.csv", return_window=36)

    def test_final_gate_requires_reserve_and_limits_overlap(self):
        estimate = estimate_from_prices(PROJECT_DIR / "prices.csv")
        selected = ("VOO", "VTI", "VNQ", "VWO", "FBND", "SGOV")
        indices = [estimate["assets"].index(asset) for asset in selected]
        covariance = covariance_matrix(
            (estimate["volatilities"][index] for index in indices),
            ((estimate["correlations"][left][right] for right in indices) for left in indices),
        )
        groups = overlap_groups_for_assets(selected)
        expected = (0.08, 0.08, 0.06, 0.07, 0.045, 0.035)
        no_reserve = search_lowest_risk_mix(
            expected, covariance, 0.065,
            (False,) * len(selected), 0.01,
            overlap_groups=groups, max_overlap_weight=0.60, max_asset_weight=0.40, step=0.10,
        )
        self.assertIsNone(no_reserve)
        with_sgov = search_lowest_risk_mix(
            expected, covariance, 0.065,
            (False,) * 5 + (True,), 0.01,
            overlap_groups=groups, max_overlap_weight=0.60, max_asset_weight=0.40, step=0.10,
        )
        self.assertIsNotNone(with_sgov)
        self.assertLessEqual(max(with_sgov["weights"]), 0.40)
        self.assertLessEqual(max(overlap_bucket_weights(with_sgov["weights"], groups).values()), 0.60)

    def test_no_modeled_candidates_and_pairwise_overlap_screen(self):
        estimate = extend_estimate_with_candidates(estimate_from_prices(PROJECT_DIR / "prices.csv"))
        self.assertEqual(available_assets(("TLT", "VTI")), ("TLT", "VTI"))
        self.assertEqual(estimate["modeled_assets"], ())
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
            tuple(SCENARIO_EXPECTED_RETURNS[asset] for asset in estimate["assets"]), covariance, 0.065,
            tuple(asset == "SGOV" for asset in estimate["assets"]), 0.03,
            step=0.10,
            allow_shorting=True,
            max_short_weight=0.10,
            max_gross_exposure=1.10,
            max_asset_weight=0.40,
            asset_caps=tuple(0.10 if asset == "FBTC" else 1.0 for asset in estimate["assets"]),
        )
        self.assertIsNotNone(result)
        self.assertGreaterEqual(min(result["weights"]), -0.10)
        self.assertLessEqual(sum(abs(weight) for weight in result["weights"]), 1.10)
        self.assertLessEqual(result["weights"][estimate["assets"].index("FBTC")], 0.10)

    def test_inverse_mandate_uses_fixed_weights_and_never_invents_reserve(self):
        weights = (0.45, 0.35, 0.20)
        bounds = mandate_boundaries(
            weights, ("VOO", "VTI", "SGOV"), (0.08, 0.08, 0.035),
            covariance_matrix((0.12, 0.13, 0.005), ((1, 0.95, 0), (0.95, 1, 0), (0, 0, 1))),
            (False, False, True), ("U.S. equity beta", "U.S. equity beta", "Treasury/cash"),
            ((1, 0.95, 0), (0.95, 1, 0), (0, 0, 1)),
            {asset: (0.01, -0.02, 0.03) for asset in ("VOO", "VTI", "SGOV")},
        )
        self.assertAlmostEqual(bounds["maximum_return_target"], 0.071)
        self.assertAlmostEqual(bounds["maximum_reserve_floor"], 0.20)
        self.assertAlmostEqual(bounds["minimum_bucket_cap"], 0.80)
        self.assertAlmostEqual(bounds["minimum_pair_cap"], 0.80)
        limits = dict(return_target=0.07, reserve_floor=0.01, ticker_cap=0.50, bitcoin_cap=0.10,
                      short_allowance=0, gross_cap=1, bucket_cap=0.80, pair_cap=0.80,
                      drawdown_tolerance=0.30)
        self.assertTrue(numerical_mandate_pass(bounds, limits))
        self.assertFalse(numerical_mandate_pass(bounds, {**limits, "bucket_cap": 0.60}))

    def test_auto_pass_preserves_reserve_and_risk_caps(self):
        assets = ("VOO", "FBTC", "SGOV")
        result = best_numerical_mix(
            assets=assets, expected_returns=(0.08, 0.12, 0.035),
            covariance=covariance_matrix((0.12, 0.4, 0.005), ((1, 0, 0), (0, 1, 0), (0, 0, 1))),
            reserve_eligible=(False, False, True),
            overlap_groups=("U.S. equity beta", "Digital asset beta", "Treasury/cash"),
            correlation=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            monthly_returns={asset: (0.01, -0.02, 0.03) for asset in assets},
            reserve_floor=0.10, ticker_cap=0.60, bitcoin_cap=0.10,
            bucket_cap=0.60, pair_cap=0.70, correlation_threshold=0.70,
            drawdown_tolerance=0.30, allow_shorting=False,
            short_allowance=0.0, gross_cap=1.0, step=0.10,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["weights"], (0.6, 0.1, 0.3))
        self.assertAlmostEqual(result["expected_return"], 0.0705)
        self.assertAlmostEqual(usable_return_target(0.09, result["expected_return"]), 0.07)

    def test_full_process_check_does_not_turn_failure_or_review_into_pass(self):
        rows = [
            {"Gate": "Annual turnover", "Result": "FAIL", "Evidence": "400% / 25%"},
            {"Gate": "Frozen holdout", "Result": "FAIL", "Evidence": "Net trails buy-and-hold"},
            {"Gate": "Return data quality", "Result": "REVIEW", "Evidence": "Distributions excluded"},
            {"Gate": "Reserve eligibility", "Result": "PASS", "Evidence": "SGOV observed"},
        ]
        report = full_process_pass_report(rows)
        self.assertFalse(report["ready"])
        self.assertEqual((report["fail_count"], report["review_count"]), (2, 1))
        self.assertEqual({row["Gate"] for row in report["blockers"]}, {
            "Annual turnover", "Frozen holdout", "Return data quality"
        })
        self.assertEqual(rows[0]["Result"], "FAIL")


if __name__ == "__main__":
    unittest.main()

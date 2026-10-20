import unittest
from dataclasses import replace

from project1_model import (
    AcquisitionInputs,
    BASE,
    MARKET_PRICE,
    acquisition_overlay,
    committee_decision,
    comparable_company_evidence,
    market_expectations_dashboard,
    run_model,
    run_industry_regimes,
    run_named_scenarios,
)


class ProjectOneModelTests(unittest.TestCase):
    def test_base_statements_articulate_and_cash_ties(self):
        result = run_model(BASE)
        self.assertTrue(all(result["checks"].values()))
        for row in result["forecasts"]:
            self.assertAlmostEqual(row["balance_gap"], 0.0, places=6)
            self.assertAlmostEqual(row["cash_flow_tie_gap"], 0.0, places=6)

    def test_value_falls_when_wacc_rises(self):
        base_value = run_model(BASE)["valuation"]["value_per_share"]
        higher_wacc_value = run_model(replace(BASE, wacc=0.11))["valuation"][
            "value_per_share"
        ]
        self.assertLess(higher_wacc_value, base_value)

    def test_value_rises_when_terminal_growth_rises(self):
        base_value = run_model(BASE)["valuation"]["value_per_share"]
        higher_growth_value = run_model(
            replace(BASE, terminal_growth=0.035)
        )["valuation"]["value_per_share"]
        self.assertGreater(higher_growth_value, base_value)

    def test_named_scenarios_are_ordered(self):
        results = run_named_scenarios()
        downside = results["Downside"]["valuation"]["value_per_share"]
        base = results["Base"]["valuation"]["value_per_share"]
        upside = results["Upside"]["valuation"]["value_per_share"]
        self.assertLess(downside, base)
        self.assertLess(base, upside)

    def test_terminal_growth_must_be_below_wacc(self):
        with self.assertRaisesRegex(ValueError, "Terminal growth must be below WACC"):
            run_model(replace(BASE, terminal_growth=BASE.wacc))

    def test_enterprise_value_peer_multiple_and_bridge(self):
        peer = comparable_company_evidence()
        self.assertAlmostEqual(peer["peer_ev_to_revenue"], 9.12491094, places=7)
        self.assertAlmostEqual(peer["implied_value_per_share"], 189.64183177, places=7)
        self.assertGreater(peer["target_ev_to_revenue"], peer["peer_ev_to_revenue"])

    def test_committee_decision_uses_calculated_value(self):
        base = run_model(BASE)
        stressed = run_model(
            replace(
                BASE,
                revenue_growth=tuple(growth - 0.05 for growth in BASE.revenue_growth),
                wacc=0.13,
            )
        )
        self.assertEqual(
            committee_decision(base)["action"],
            "Watch/defer - no position at the current market price",
        )
        self.assertEqual(committee_decision(stressed)["action"], "Do not initiate")

        artificial_initiate = {
            "valuation": {"value_per_share": MARKET_PRICE * 1.16},
            "checks": {"integrity": True},
        }
        self.assertEqual(
            committee_decision(artificial_initiate)["action"], "Initiate"
        )

    def test_market_expectations_dashboard_reconciles_price(self):
        dashboard = market_expectations_dashboard(BASE)
        shift = dashboard["implied_growth_shift"]
        self.assertIsNotNone(shift)
        shifted_value = run_model(
            replace(
                BASE,
                revenue_growth=tuple(growth + shift for growth in BASE.revenue_growth),
            )
        )["valuation"]["value_per_share"]
        self.assertAlmostEqual(shifted_value, MARKET_PRICE, places=6)
        self.assertLess(dashboard["bounded_value"], MARKET_PRICE)
        required_shifts = [
            row["growth_shift"] for row in dashboard["feasibility"]
        ]
        self.assertEqual(required_shifts, sorted(required_shifts))

    def test_industry_regimes_jointly_stress_operations_and_beta(self):
        regimes = run_industry_regimes()
        values = {
            row["name"]: row["result"]["valuation"]["value_per_share"]
            for row in regimes
        }
        self.assertLess(values["Cycle reversal"], values["Orderly normalization"])
        self.assertLess(values["Orderly normalization"], values["AI buildout extends"])
        boom = next(row for row in regimes if row["name"] == "AI buildout extends")
        self.assertGreater(boom["inputs"].wacc, BASE.wacc)

    def test_acquisition_overlay_is_separate_and_monotonic(self):
        base = run_model(BASE)
        overlay = acquisition_overlay(base)
        stronger = acquisition_overlay(
            base,
            replace(
                AcquisitionInputs(),
                ebita_margin=(0.20, 0.23, 0.26, 0.29, 0.31),
            ),
        )
        self.assertEqual(base["valuation"]["value_per_share"], run_model(BASE)["valuation"]["value_per_share"])
        self.assertGreater(
            stronger["acquired_enterprise_value"], overlay["acquired_enterprise_value"]
        )
        self.assertAlmostEqual(
            overlay["combined_value_per_share"]
            - base["valuation"]["value_per_share"],
            overlay["per_share_effect"],
            places=7,
        )

    def test_acquisition_terminal_growth_must_be_below_wacc(self):
        with self.assertRaisesRegex(
            ValueError, "Acquisition terminal growth must be below acquisition WACC"
        ):
            acquisition_overlay(
                run_model(BASE),
                replace(AcquisitionInputs(), terminal_growth=0.105),
            )


if __name__ == "__main__":
    unittest.main()

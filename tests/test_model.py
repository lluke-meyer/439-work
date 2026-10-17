import unittest
from dataclasses import replace

from project1_model import BASE, run_model, run_named_scenarios


class ProjectOneModelTests(unittest.TestCase):
    def test_base_statements_articulate_and_cash_ties(self):
        result = run_model(BASE)
        self.assertTrue(all(result["checks"].values()))
        for row in result["forecasts"]:
            self.assertAlmostEqual(row["balance_gap"], 0.0, places=6)
            self.assertAlmostEqual(row["cash_flow_tie_gap"], 0.0, places=6)

    def test_value_falls_when_wacc_rises(self):
        base_value = run_model(BASE)["valuation"]["value_per_share"]
        higher_wacc_value = run_model(replace(BASE, wacc=0.10))["valuation"][
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


if __name__ == "__main__":
    unittest.main()

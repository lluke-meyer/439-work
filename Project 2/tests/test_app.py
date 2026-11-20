import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


PROJECT_DIR = Path(__file__).resolve().parents[1]


class Project2AppTests(unittest.TestCase):
    def test_app_renders_without_exceptions(self):
        app = AppTest.from_file(str(PROJECT_DIR / "app.py"))
        app.run(timeout=30)
        self.assertEqual([], list(app.exception))
        self.assertEqual([], list(app.error))
        self.assertGreaterEqual(len(app.dataframe), 4)
        fund_slots = next(widget for widget in app.selectbox if widget.label == "Fund slots")
        self.assertEqual([int(value) for value in fund_slots.options], list(range(3, 11)))
        themes = next(widget for widget in app.selectbox if widget.label == "Starting six-fund theme")
        self.assertEqual(len(themes.options), 11)  # custom/current plus ten themes
        self.assertEqual(app.multiselect[0].value, ["VOO", "VTI", "VNQ", "VWO", "FBTC", "FBND", "FIVA", "SGOV", "TLT", "TIP"])
        window = next(widget for widget in app.selectbox if widget.label == "Estimation window")
        self.assertEqual(list(window.options), ["Full available history", "Last 24 monthly returns"])
        theme_table = next(table.value for table in app.dataframe if "Theme" in table.value.columns)
        self.assertEqual(len(theme_table), 10)
        self.assertTrue(set(theme_table["Allocation verdict"]).issubset({"PASS", "NO FEASIBLE MIX"}))
        gate_table = next(table.value for table in app.dataframe if "Gate" in table.value.columns)
        drawdown = gate_table.loc[gate_table["Gate"] == "Historical drawdown", "Result"].iloc[0]
        self.assertIn(drawdown, ("PASS", "FAIL"))
        summary = next(item.value for item in app.markdown if item.value.startswith('<div class="p2-summary-grid"'))
        self.assertIn("NO FEASIBLE MIX", summary)
        self.assertIn("REJECT / REDESIGN", summary)
        self.assertIn("Committee walkthrough: how to assess this portfolio", [item.label for item in app.expander])
        verdict = next(item.value for item in app.markdown if item.value.startswith('<div class="p2-verdict-bar"'))
        self.assertIn("NO FEASIBLE MIX", verdict)
        self.assertIn("REJECT / REDESIGN", verdict)
        boundary_table = next(table.value for table in app.dataframe if "Chosen mix requires" in table.value.columns)
        self.assertEqual(len(boundary_table), 9)
        self.assertEqual(boundary_table.loc[boundary_table["Mandate control"] == "Bitcoin cap", "Current check"].iloc[0], "PASS")
        self.assertEqual(boundary_table.loc[boundary_table["Mandate control"] == "Return target", "Current check"].iloc[0], "FAIL")
        self.assertEqual([], list(app.exception))
        next(widget for widget in app.button if widget.label == "Auto full-process pass check").click().run(timeout=60)
        self.assertEqual([], list(app.exception))
        self.assertTrue(any("Full-process Auto-Pass unavailable" in item.value for item in app.warning))
        blocker_table = next(table.value for table in app.dataframe if "Needed for a real pass" in table.value.columns)
        self.assertIn("Frozen holdout", set(blocker_table["Gate"]))
        self.assertIn("Annual turnover", set(blocker_table["Gate"]))
        next(widget for widget in app.button if widget.label == "Auto-Pass numerical mandate").click().run(timeout=90)
        self.assertEqual([], list(app.exception))
        self.assertEqual(next(widget.value for widget in app.number_input if widget.label == "Objective return (%)"), 7.7)
        self.assertTrue(any("Auto-Pass applied" in item.value for item in app.success))
        self.assertEqual(next(widget.value for widget in app.number_input if widget.label == "FBTC chosen weight (%)"), 10.0)
        summary = next(item.value for item in app.markdown if item.value.startswith('<div class="p2-summary-grid"'))
        self.assertIn("<strong>PASS</strong>", summary)
        self.assertIn("REJECT / REDESIGN", summary)
        next(widget for widget in app.button if widget.label == "Restore inputs before Auto-Pass").click().run(timeout=90)
        self.assertEqual(next(widget.value for widget in app.number_input if widget.label == "Objective return (%)"), 9.0)
        self.assertEqual(next(widget.value for widget in app.number_input if widget.label == "VOO chosen weight (%)"), 10.0)
        self.assertFalse(any("Auto-Pass applied" in item.value for item in app.success))
        next(widget for widget in app.number_input if widget.label == "Objective return (%)").set_value(7.5).run(timeout=60)
        summary = next(item.value for item in app.markdown if item.value.startswith('<div class="p2-summary-grid"'))
        self.assertIn("<strong>PASS</strong>", summary)
        self.assertIn("REJECT / REDESIGN", summary)
        verdict = next(item.value for item in app.markdown if item.value.startswith('<div class="p2-verdict-bar"'))
        self.assertIn('class="p2-verdict-value pass">PASS', verdict)
        self.assertIn("REJECT / REDESIGN", verdict)
        window = next(widget for widget in app.selectbox if widget.label == "Estimation window")
        window.set_value("Last 24 monthly returns").run(timeout=90)
        self.assertEqual([], list(app.exception))
        self.assertTrue(any("24 monthly price changes" in item.value for item in app.markdown))


if __name__ == "__main__":
    unittest.main()

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
        self.assertEqual(app.multiselect[0].value, ["TLT", "SOXX", "VTI", "VXUS", "FREL", "GBTC"])
        theme_table = next(table.value for table in app.dataframe if "Theme" in table.value.columns)
        self.assertEqual(len(theme_table), 10)
        self.assertTrue(set(theme_table["Allocation verdict"]).issubset({"PASS", "NO FEASIBLE MIX"}))
        gate_table = next(table.value for table in app.dataframe if "Gate" in table.value.columns)
        drawdown = gate_table.loc[gate_table["Gate"] == "Historical drawdown", "Result"].iloc[0]
        self.assertEqual(drawdown, "PASS")
        self.assertEqual(next(metric.value for metric in app.metric if metric.label == "Allocation mandate"), "PASS")


if __name__ == "__main__":
    unittest.main()

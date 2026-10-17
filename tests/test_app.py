import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class ProjectOneAppTests(unittest.TestCase):
    def test_base_page_loads_without_exception(self):
        app = AppTest.from_file(APP_PATH, default_timeout=30).run()
        self.assertEqual(list(app.exception), [])
        self.assertEqual(app.title[0].value, "Cadence Design Systems Valuation Workbench")
        self.assertEqual(app.selectbox[0].value, "Base")
        metrics = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(metrics["Intrinsic value"], "$97.28")
        self.assertEqual(metrics["Market price"], "$313.04")

    def test_failure_demo_fails_loudly(self):
        app = AppTest.from_file(APP_PATH, default_timeout=30).run()
        app.checkbox[0].check().run()
        self.assertIn(
            "EXPECTED FAILURE: Terminal growth must be below WACC.",
            [error.value for error in app.error],
        )

    def test_downside_changes_committee_action(self):
        app = AppTest.from_file(APP_PATH, default_timeout=30).run()
        app.selectbox[0].select("Downside").run()
        actions = [
            message.value
            for message in app.success
            if str(message.value).startswith("Committee action")
        ]
        self.assertEqual(actions, ["Committee action: Do not initiate"])


if __name__ == "__main__":
    unittest.main()

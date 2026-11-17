import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

import market_data  # noqa: E402
from portfolio import estimate_from_prices  # noqa: E402


class MarketDataTests(unittest.TestCase):
    def test_public_adapter_returns_model_csv_shape_without_network(self):
        dates = [
            f"{year}-{month:02d}-01"
            for year in (2023, 2024, 2025, 2026)
            for month in range(1, 13)
        ]
        fake_history = {
            ticker: {date: 100.0 + index + len(ticker) for index, date in enumerate(dates)}
            for ticker in ("VTI", "SGOV")
        }
        with patch.object(market_data, "_fetch_monthly_series", side_effect=lambda ticker, lookback_years, timeout: fake_history[ticker]):
            csv_text = market_data.fetch_yahoo_monthly_csv(("VTI", "SGOV"), lookback_years=3)
        estimate = estimate_from_prices(io.StringIO(csv_text))
        self.assertEqual(estimate["assets"], ("VTI", "SGOV"))
        self.assertEqual(estimate["return_observations"], 47)


if __name__ == "__main__":
    unittest.main()

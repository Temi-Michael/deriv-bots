import unittest
from unittest.mock import AsyncMock
import pandas as pd
from src.bot import HigherLowerBot

class TestHigherLowerBot(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = HigherLowerBot(
            token="test",
            app_id="1089",
            symbol="R_100",
            duration=5,
            duration_unit="t",
            stake=1.0,
            take_profit=10.0,
            stop_loss=10.0,
            martingale_mult=2.0,
            max_martingale_level=3,
            barrier_offset=0.5
        )
        self.bot.send = AsyncMock()
        self.bot.place_trade = AsyncMock()

    async def test_evaluate_strategy_lower(self):
        # High touches upper BB
        self.bot.calculate_indicators = lambda: (
            {'high': 105.0, 'low': 100.0}, # Current candle
            104.0, # Upper BB
            96.0   # Lower BB
        )
        await self.bot.evaluate_strategy()
        # Should place PUT with +0.5 barrier
        self.bot.place_trade.assert_called_once_with("PUT", "+0.5")

    async def test_evaluate_strategy_higher(self):
        # Low touches lower BB
        self.bot.calculate_indicators = lambda: (
            {'high': 100.0, 'low': 95.0}, # Current candle
            104.0, # Upper BB
            96.0   # Lower BB
        )
        await self.bot.evaluate_strategy()
        # Should place CALL with -0.5 barrier
        self.bot.place_trade.assert_called_once_with("CALL", "-0.5")

if __name__ == "__main__":
    unittest.main()

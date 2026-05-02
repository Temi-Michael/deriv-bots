import unittest
from unittest.mock import AsyncMock
import pandas as pd
from src.bot import AccumulatorBot

class TestAccumulatorBot(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = AccumulatorBot(
            token="test",
            app_id="1089",
            symbol="R_100",
            growth_rate=0.01,
            stake=1.0,
            take_profit=10.0,
            stop_loss=10.0,
            tick_exit_count=5,
            martingale_mult=2.0,
            max_martingale_level=3
        )
        self.bot.send = AsyncMock()
        self.bot.place_trade = AsyncMock()

    async def test_evaluate_strategy_entry(self):
        # Ranging market (ADX < 20)
        self.bot.calculate_indicators = lambda: 15.0
        await self.bot.evaluate_strategy()
        self.bot.place_trade.assert_called_once()

    async def test_evaluate_strategy_no_entry(self):
        # Trending market (ADX > 20)
        self.bot.calculate_indicators = lambda: 30.0
        await self.bot.evaluate_strategy()
        self.bot.place_trade.assert_not_called()

    async def test_auto_exit_tick_count(self):
        self.bot.current_contract_id = 12345
        self.bot.current_tick_count = 4

        # Simulating the 5th tick coming in
        contract_update = {
            "is_sold": 0,
            "tick_count": 5,
            "profit": 0.50
        }
        await self.bot.handle_open_contract_update(contract_update)

        # It should send the sell request because tick_count (5) >= tick_exit_count (5)
        self.bot.send.assert_called_with({"sell": 12345, "price": 0})

if __name__ == "__main__":
    unittest.main()

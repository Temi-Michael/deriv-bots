import unittest
from unittest.mock import AsyncMock
import pandas as pd
from src.bot import RiseFallBot

class TestRiseFallBot(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = RiseFallBot(
            token="test",
            app_id="1089",
            symbol="R_100",
            duration=5,
            duration_unit="t",
            stake=1.0,
            take_profit=10.0,
            stop_loss=10.0,
            martingale_mult=2.0,
            max_martingale_level=3
        )
        self.bot.send = AsyncMock()
        self.bot.place_trade = AsyncMock()

    def test_indicator_calculation_insufficient_data(self):
        # Need at least 25 candles
        self.bot.candle_data = pd.DataFrame({'close': [100] * 10})
        curr, prev, ema8, ema21 = self.bot.calculate_indicators()
        self.assertIsNone(curr)

    async def test_evaluate_strategy_call(self):
        # Mock data so that EMA 8 crosses above EMA 21, and RSI > 55
        self.bot.calculate_indicators = lambda: (
            {'ema_8': 105, 'ema_21': 100, 'rsi_14': 60}, # Current
            {'ema_8': 95, 'ema_21': 100, 'rsi_14': 50},  # Previous
            None, None
        )
        await self.bot.evaluate_strategy()
        self.bot.place_trade.assert_called_once_with("CALL")

    async def test_evaluate_strategy_put(self):
        # Mock data so that EMA 8 crosses below EMA 21, and RSI < 45
        self.bot.calculate_indicators = lambda: (
            {'ema_8': 95, 'ema_21': 100, 'rsi_14': 40}, # Current
            {'ema_8': 105, 'ema_21': 100, 'rsi_14': 50},  # Previous
            None, None
        )
        await self.bot.evaluate_strategy()
        self.bot.place_trade.assert_called_once_with("PUT")

    async def test_martingale_max_level(self):
        self.bot.current_martingale_level = 3
        self.bot.max_martingale_level = 3
        self.bot.current_stake = 8.0

        contract = {"profit": -8.0, "status": "lost"}
        await self.bot.handle_contract_close(contract)

        # Should stop the bot to prevent liquidation
        self.assertFalse(self.bot.is_running)

    async def test_stop_loss_trigger(self):
        self.bot.is_running = True
        contract = {"profit": -15.0, "status": "lost"}
        await self.bot.handle_contract_close(contract)

        # Session P/L = -15, which is <= -10 (stop loss)
        self.assertFalse(self.bot.is_running)

if __name__ == "__main__":
    unittest.main()

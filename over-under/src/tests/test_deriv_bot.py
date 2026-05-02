import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from src.deriv_bot import DerivBot

class TestDerivBot(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.bot = DerivBot(
            token="test_token",
            app_id="1089",
            symbol="R_100",
            tick_window=5,
            duration=1,
            stake=1.0,
            take_profit=10.0,
            max_runs=0,
            strategy_mode=1,
            use_martingale=True,
            martingale_multiplier=2.5,
            max_martingale_level=3
        )
        self.bot.ws = AsyncMock()
        self.bot.send = AsyncMock()

    def test_extract_last_digit(self):
        self.bot.decimal_places = 2
        # For price 123.45, digit should be 5
        self.assertEqual(self.bot.extract_last_digit("123.45"), 5)
        # Avoid float trailing issue
        self.assertEqual(self.bot.extract_last_digit("123.40"), 0)

        self.bot.decimal_places = 3
        self.assertEqual(self.bot.extract_last_digit("123.456"), 6)

    async def test_evaluate_strategy_mode1_over(self):
        self.bot.strategy_mode = 1
        self.bot.digit_history = [1, 2, 5, 6, 8] # Median is 5
        self.bot.place_trade = AsyncMock()
        await self.bot.evaluate_strategy()
        self.bot.place_trade.assert_called_once_with("OVER", 3)

    async def test_evaluate_strategy_mode1_under(self):
        self.bot.strategy_mode = 1
        self.bot.digit_history = [1, 2, 3, 6, 8] # Median is 3
        self.bot.place_trade = AsyncMock()
        await self.bot.evaluate_strategy()
        self.bot.place_trade.assert_called_once_with("UNDER", 6)

    async def test_evaluate_strategy_mode2(self):
        self.bot.strategy_mode = 2
        self.bot.digit_history = [9, 8, 3, 2, 1] # Last 3 are <= 3
        self.bot.place_trade = AsyncMock()
        await self.bot.evaluate_strategy()
        self.bot.place_trade.assert_called_once_with("OVER", 3)

        # Test no trigger
        self.bot.place_trade.reset_mock()
        self.bot.digit_history = [9, 8, 3, 2, 5] # Last is 5
        await self.bot.evaluate_strategy()
        self.bot.place_trade.assert_not_called()

    async def test_evaluate_strategy_mode3(self):
        self.bot.strategy_mode = 3
        self.bot.digit_history = [1, 2, 6, 7, 8] # Last 3 are >= 6
        self.bot.place_trade = AsyncMock()
        await self.bot.evaluate_strategy()
        self.bot.place_trade.assert_called_once_with("UNDER", 6)

    async def test_martingale_loss(self):
        # Simulate a loss
        contract = {"profit": -1.0, "status": "lost"}
        await self.bot.handle_contract_close(contract)

        self.assertEqual(self.bot.current_martingale_level, 1)
        self.assertEqual(self.bot.current_stake, 2.5) # 1.0 * 2.5
        self.assertEqual(self.bot.session_pl, -1.0)

        # Second loss
        contract = {"profit": -2.5, "status": "lost"}
        await self.bot.handle_contract_close(contract)

        self.assertEqual(self.bot.current_martingale_level, 2)
        self.assertEqual(self.bot.current_stake, 6.25) # 2.5 * 2.5 = 6.25 (rounded)
        self.assertEqual(self.bot.session_pl, -3.5)

    async def test_martingale_win_reset(self):
        self.bot.current_stake = 6.25
        self.bot.current_martingale_level = 2

        contract = {"profit": 5.0, "status": "won"}
        await self.bot.handle_contract_close(contract)

        self.assertEqual(self.bot.current_martingale_level, 0)
        self.assertEqual(self.bot.current_stake, 1.0) # Reset to initial stake

    async def test_take_profit_stop(self):
        self.bot.is_running = True
        contract = {"profit": 15.0, "status": "won"} # >= take_profit of 10.0
        await self.bot.handle_contract_close(contract)

        self.assertFalse(self.bot.is_running)

if __name__ == '__main__':
    unittest.main()

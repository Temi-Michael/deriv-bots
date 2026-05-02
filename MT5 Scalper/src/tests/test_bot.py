import unittest
import pandas as pd
from src.bot import ScalperBot
from src.mock_mt5 import MockMT5

class TestScalperBot(unittest.TestCase):
    def setUp(self):
        self.mt5 = MockMT5()
        self.bot = ScalperBot(mt5_module=self.mt5, symbol="EURUSD")
        self.bot.start()

    def tearDown(self):
        self.bot.stop()

    def test_initialization(self):
        self.assertTrue(self.mt5.is_initialized)

    def test_get_data(self):
        df = self.bot.get_data(count=100)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 100)
        self.assertTrue('close' in df.columns)
        self.assertTrue('time' in df.columns)

    def test_calculate_indicators(self):
        df = self.bot.get_data(count=100)
        df_ind = self.bot.calculate_indicators(df)
        self.assertIsNotNone(df_ind)
        self.assertTrue('ema' in df_ind.columns)
        self.assertTrue('stoch_k' in df_ind.columns)
        self.assertTrue('atr' in df_ind.columns)

    def test_check_signals_buy(self):
        # Create a mock dataframe for a BUY signal
        # Price > EMA, Stoch crosses above 20
        data = {
            'close': [1.1000, 1.1050],
            'ema': [1.0900, 1.0900], # Price is > EMA
            'stoch_k': [15.0, 25.0], # Crossed 20
            'atr': [0.0010, 0.0010]
        }
        df = pd.DataFrame(data)
        signal = self.bot.check_signals(df)
        self.assertEqual(signal, 1)

    def test_check_signals_sell(self):
        # Create a mock dataframe for a SELL signal
        # Price < EMA, Stoch crosses below 80
        data = {
            'close': [1.0900, 1.0850],
            'ema': [1.1000, 1.1000], # Price is < EMA
            'stoch_k': [85.0, 75.0], # Crossed below 80
            'atr': [0.0010, 0.0010]
        }
        df = pd.DataFrame(data)
        signal = self.bot.check_signals(df)
        self.assertEqual(signal, -1)

    def test_open_trade(self):
        # Manually trigger a trade
        data = {
            'close': [1.1000, 1.1050],
            'ema': [1.0900, 1.0900],
            'stoch_k': [15.0, 25.0],
            'atr': [0.0010, 0.0010]
        }
        df = pd.DataFrame(data)
        self.bot.open_trade(1, df)

        # Verify position was opened
        positions = self.mt5.positions_get(symbol="EURUSD")
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].type, self.bot.ORDER_TYPE_BUY)

if __name__ == '__main__':
    unittest.main()

import pandas as pd
import numpy as np
import ta
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MT5Bot')

class ScalperBot:
    def __init__(self, mt5_module, symbol="EURUSD", lot=0.1, ema_period=50, stoch_k=14, stoch_d=3, atr_period=14):
        self.mt5 = mt5_module
        self.symbol = symbol
        self.lot = lot
        self.ema_period = ema_period
        self.stoch_k = stoch_k
        self.stoch_d = stoch_d
        self.atr_period = atr_period

        # MT5 Constants
        self.ORDER_TYPE_BUY = 0
        self.ORDER_TYPE_SELL = 1
        self.TRADE_ACTION_DEAL = 1

    def start(self):
        if not self.mt5.initialize():
            logger.error("initialize() failed")
            return False
        logger.info(f"Initialized bot for {self.symbol}")
        return True

    def stop(self):
        self.mt5.shutdown()
        logger.info("Bot shut down")

    def get_data(self, count=100):
        try:
            # Get M1 timeframe data
            timeframe = getattr(self.mt5, 'TIMEFRAME_M1', 1)
            rates = self.mt5.copy_rates_from_pos(self.symbol, timeframe, 0, count)
            if rates is None or len(rates) == 0:
                logger.warning(f"Failed to get data for {self.symbol}")
                return None
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None

    def calculate_indicators(self, df):
        if df is None or len(df) < max(self.ema_period, self.atr_period, self.stoch_k) + 1:
            return None

        df['ema'] = ta.trend.ema_indicator(df['close'], window=self.ema_period)

        # Stochastic
        stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], window=self.stoch_k, smooth_window=self.stoch_d)
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()

        # ATR
        df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=self.atr_period)

        return df

    def check_signals(self, df):
        if df is None or len(df) < 2:
            return 0 # 0: None, 1: Buy, -1: Sell

        # Current and previous candle
        curr = df.iloc[-1]
        prev = df.iloc[-2]

        # Buy Signal: Price > EMA, Stoch crosses above 20 (oversold)
        if curr['close'] > curr['ema'] and prev['stoch_k'] < 20 and curr['stoch_k'] > prev['stoch_k']:
            return 1

        # Sell Signal: Price < EMA, Stoch crosses below 80 (overbought)
        if curr['close'] < curr['ema'] and prev['stoch_k'] > 80 and curr['stoch_k'] < prev['stoch_k']:
            return -1

        return 0

    def open_trade(self, signal, df):
        if signal == 0:
            return

        # Check if already have positions
        positions = self.mt5.positions_get(symbol=self.symbol)
        if positions is None:
            logger.error("Failed to get positions")
            return

        if len(positions) > 0:
            logger.info("Already have an open position, skipping.")
            return

        tick = self.mt5.symbol_info_tick(self.symbol)
        if not tick:
            logger.error("Failed to get tick data")
            return

        curr_atr = df.iloc[-1]['atr']

        if signal == 1:
            order_type = self.ORDER_TYPE_BUY
            price = tick.ask
            sl = price - (curr_atr * 1.5)
            tp = price + (curr_atr * 2.0)
            logger.info("Sending BUY request")
        elif signal == -1:
            order_type = self.ORDER_TYPE_SELL
            price = tick.bid
            sl = price + (curr_atr * 1.5)
            tp = price - (curr_atr * 2.0)
            logger.info("Sending SELL request")

        request = {
            "action": self.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "magic": 123456,
            "comment": "Scalper Bot",
            "type_time": 0, # ORDER_TIME_GTC
            "type_filling": 0, # ORDER_FILLING_FOK
        }

        result = self.mt5.order_send(request)
        if result and getattr(result, 'retcode', -1) == 10009: # TRADE_RETCODE_DONE
            logger.info(f"Order opened successfully. Ticket: {result.order}")
        else:
            logger.error(f"Order failed: {result}")

    def run_cycle(self):
        logger.info("Running bot cycle...")
        df = self.get_data()
        if df is not None:
            df = self.calculate_indicators(df)
            if df is not None:
                signal = self.check_signals(df)
                if signal != 0:
                    self.open_trade(signal, df)
                else:
                    logger.info("No signal generated.")

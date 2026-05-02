import random
import time
import pandas as pd
from datetime import datetime, timedelta

class MockMT5:
    """Mock environment for testing MT5 without Windows or MT5 installed."""

    def __init__(self):
        self.is_initialized = False
        self._mock_price = 1.10000
        self._positions = []
        self.TIMEFRAME_M1 = 1

    def initialize(self):
        self.is_initialized = True
        return True

    def shutdown(self):
        self.is_initialized = False
        self._positions.clear()

    def copy_rates_from_pos(self, symbol, timeframe, start_pos, count):
        """Generates random price walks simulating M1 candles."""
        if not self.is_initialized:
            return None

        rates = []
        now = datetime.now()
        now = now.replace(second=0, microsecond=0) # Round to minute

        current_time = now - timedelta(minutes=count)

        for i in range(count):
            open_price = self._mock_price
            close_price = open_price + random.uniform(-0.0005, 0.0005)
            high_price = max(open_price, close_price) + random.uniform(0, 0.0002)
            low_price = min(open_price, close_price) - random.uniform(0, 0.0002)

            rates.append((
                int(current_time.timestamp()),
                open_price,
                high_price,
                low_price,
                close_price,
                100, # tick_volume
                0,   # spread
                0    # real_volume
            ))
            self._mock_price = close_price
            current_time += timedelta(minutes=1)

        # Convert to numpy array with named fields
        import numpy as np
        dtype = [('time', 'i8'), ('open', 'f8'), ('high', 'f8'), ('low', 'f8'), ('close', 'f8'), ('tick_volume', 'i8'), ('spread', 'i4'), ('real_volume', 'i8')]
        return np.array(rates, dtype=dtype)

    def order_send(self, request):
        if not self.is_initialized:
            return None

        # Simulate an order
        # request is a dict
        action = request.get('action')
        symbol = request.get('symbol')
        volume = request.get('volume')
        type_ = request.get('type') # 0: BUY, 1: SELL
        price = request.get('price', self._mock_price)
        sl = request.get('sl')
        tp = request.get('tp')

        order_id = random.randint(1000000, 9999999)

        class Result:
            pass
        res = Result()
        res.retcode = 10009 # TRADE_RETCODE_DONE
        res.order = order_id
        res.volume = volume
        res.price = price

        self._positions.append({
            'ticket': order_id,
            'symbol': symbol,
            'type': type_,
            'volume': volume,
            'price_open': price,
            'sl': sl,
            'tp': tp,
            'time': int(time.time())
        })

        return res

    def positions_get(self, symbol=None):
        if not self.is_initialized:
            return None

        class Position:
            pass

        result = []
        for p in self._positions:
            if symbol and p['symbol'] != symbol:
                continue
            pos = Position()
            pos.ticket = p['ticket']
            pos.symbol = p['symbol']
            pos.type = p['type']
            pos.volume = p['volume']
            pos.price_open = p['price_open']
            pos.sl = p['sl']
            pos.tp = p['tp']
            pos.time = p['time']
            result.append(pos)

        return result

    def symbol_info_tick(self, symbol):
        if not self.is_initialized:
            return None

        class Tick:
            pass
        tick = Tick()
        tick.ask = self._mock_price + 0.0001
        tick.bid = self._mock_price - 0.0001
        return tick

mock_mt5 = MockMT5()

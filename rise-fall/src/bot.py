import asyncio
import json
import logging
import os
import signal
from logging.handlers import RotatingFileHandler
import websockets
from colorama import init, Fore, Style
import pandas as pd
import ta

init(autoreset=True)

class RiseFallBot:
    def __init__(self, token, app_id, symbol, duration, duration_unit, stake, take_profit, stop_loss, martingale_mult, max_martingale_level):
        self.token = token
        self.app_id = app_id
        self.symbol = symbol
        self.duration = duration
        self.duration_unit = duration_unit # 't' for ticks, 's' for seconds, 'm' for minutes
        self.initial_stake = round(float(stake), 2)
        self.current_stake = self.initial_stake
        self.take_profit = float(take_profit)
        self.stop_loss = float(stop_loss)
        self.martingale_mult = float(martingale_mult)
        self.max_martingale_level = int(max_martingale_level)
        self.current_martingale_level = 0

        self.ws_url = f"wss://ws.binaryws.com/websockets/v3?app_id={self.app_id}"
        self.ws = None
        self.pip_size = None
        self.decimal_places = 2

        self.is_running = False
        self.total_trades = 0
        self.total_wins = 0
        self.total_losses = 0
        self.session_pl = 0.0

        self.current_contract_id = None
        self.candle_data = pd.DataFrame(columns=['epoch', 'open', 'high', 'low', 'close'])

        self.setup_logging()

    def setup_logging(self):
        self.logger = logging.getLogger("RiseFallBot")
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler("rise_fall.log", maxBytes=5*1024*1024, backupCount=2)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def connect(self):
        print(f"{Fore.CYAN}Connecting to Deriv API...{Style.RESET_ALL}")
        try:
            self.ws = await websockets.connect(self.ws_url)
        except Exception as e:
            print(f"{Fore.RED}Connection failed: {e}{Style.RESET_ALL}")
            return False

        await self.send({"authorize": self.token})
        auth_res = await self.receive()
        if "error" in auth_res:
            print(f"{Fore.RED}Authorization failed: {auth_res['error']['message']}{Style.RESET_ALL}")
            return False

        print(f"{Fore.GREEN}Authorized successfully!{Style.RESET_ALL}")

        await self.send({"active_symbols": "brief", "product_type": "basic"})
        sym_res = await self.receive()
        if "error" not in sym_res:
            for sym in sym_res.get("active_symbols", []):
                if sym["symbol"] == self.symbol:
                    self.pip_size = sym["pip"]
                    pip_str = f"{self.pip_size:.10f}".rstrip('0').rstrip('.')
                    self.decimal_places = len(pip_str.split('.')[-1]) if '.' in pip_str else 0
                    print(f"{Fore.CYAN}Determined pip size: {self.pip_size}{Style.RESET_ALL}")
                    break

        self.is_running = True
        return True

    async def send(self, payload):
        if self.ws:
            await self.ws.send(json.dumps(payload))
            self.logger.info(f"Sent: {payload}")

    async def receive(self):
        if self.ws:
            res = await self.ws.recv()
            data = json.loads(res)
            self.logger.info(f"Received: {data}")
            return data
        return {}

    async def fetch_historical_candles(self):
        # Fetch 60 candles of 1 minute (60 seconds)
        print(f"{Fore.YELLOW}Fetching historical M1 candles for indicators...{Style.RESET_ALL}")
        req = {
            "ticks_history": self.symbol,
            "adjust_start_time": 1,
            "count": 60,
            "end": "latest",
            "style": "candles",
            "granularity": 60
        }
        await self.send(req)

    async def subscribe_to_candles(self):
        req = {
            "ticks_history": self.symbol,
            "adjust_start_time": 1,
            "count": 1,
            "end": "latest",
            "style": "candles",
            "granularity": 60,
            "subscribe": 1
        }
        await self.send(req)

    def calculate_indicators(self):
        if len(self.candle_data) < 25: # Need at least 21 for EMA + buffer
            return None, None, None, None

        df = self.candle_data.copy()

        df['ema_8'] = ta.trend.ema_indicator(df['close'], window=8)
        df['ema_21'] = ta.trend.ema_indicator(df['close'], window=21)
        df['rsi_14'] = ta.momentum.rsi(df['close'], window=14)

        curr = df.iloc[-1]
        prev = df.iloc[-2]

        return curr, prev, df['ema_8'], df['ema_21']

    async def evaluate_strategy(self):
        if self.current_contract_id is not None:
            return # Already in a trade

        curr, prev, ema_8, ema_21 = self.calculate_indicators()

        if curr is None or pd.isna(curr['ema_21']):
            return

        # Check Cross Over Logic
        # EMA 8 crosses ABOVE EMA 21
        crossed_above = prev['ema_8'] <= prev['ema_21'] and curr['ema_8'] > curr['ema_21']
        # EMA 8 crosses BELOW EMA 21
        crossed_below = prev['ema_8'] >= prev['ema_21'] and curr['ema_8'] < curr['ema_21']

        rsi = curr['rsi_14']

        if crossed_above and rsi > 55:
            print(f"\n{Fore.MAGENTA}[SIGNAL] CALL TRIGGERED (EMA8 > EMA21, RSI: {rsi:.2f}){Style.RESET_ALL}")
            await self.place_trade("CALL")
        elif crossed_below and rsi < 45:
            print(f"\n{Fore.MAGENTA}[SIGNAL] PUT TRIGGERED (EMA8 < EMA21, RSI: {rsi:.2f}){Style.RESET_ALL}")
            await self.place_trade("PUT")

    async def place_trade(self, contract_type):
        self.current_stake = round(self.current_stake, 2)
        print(f"{Fore.BLUE}[OPEN] Placing {contract_type} | Stake: ${self.current_stake}{Style.RESET_ALL}")

        req = {
            "buy": 1,
            "price": self.current_stake,
            "parameters": {
                "amount": self.current_stake,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": self.duration,
                "duration_unit": self.duration_unit,
                "symbol": self.symbol
            }
        }
        await self.send(req)
        res = await self.receive()

        if "error" in res:
            print(f"{Fore.RED}Trade Error: {res['error']['message']}{Style.RESET_ALL}")
            return

        buy_info = res.get("buy")
        if buy_info:
            self.current_contract_id = buy_info["contract_id"]
            await self.send({"proposal_open_contract": 1, "contract_id": self.current_contract_id, "subscribe": 1})

    async def handle_contract_close(self, contract):
        profit = float(contract["profit"])
        status = contract["status"]

        self.total_trades += 1
        self.session_pl += profit

        if profit > 0:
            self.total_wins += 1
            print(f"{Fore.GREEN}[WIN] +${profit:.2f} | Session P/L: ${self.session_pl:.2f}{Style.RESET_ALL}")
            self.current_martingale_level = 0
            self.current_stake = self.initial_stake
        else:
            self.total_losses += 1
            print(f"{Fore.RED}[LOSS] ${profit:.2f} | Session P/L: ${self.session_pl:.2f}{Style.RESET_ALL}")

            if self.current_martingale_level < self.max_martingale_level:
                self.current_martingale_level += 1
                self.current_stake = round(self.current_stake * self.martingale_mult, 2)
                print(f"{Fore.YELLOW}Martingale Level {self.current_martingale_level} - Next Stake: ${self.current_stake}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}CRITICAL: Max Martingale Level ({self.max_martingale_level}) Reached! Stopping bot to prevent account liquidation.{Style.RESET_ALL}")
                self.is_running = False
                self.current_contract_id = None
                return

        self.current_contract_id = None

        # Check TP / SL
        if self.session_pl >= self.take_profit:
             print(f"\n{Fore.GREEN}Take Profit Reached (${self.take_profit})! Shutting down.{Style.RESET_ALL}")
             self.is_running = False
        elif self.session_pl <= -self.stop_loss:
             print(f"\n{Fore.RED}Stop Loss Reached (-${self.stop_loss})! Shutting down to protect capital.{Style.RESET_ALL}")
             self.is_running = False

    async def main_loop(self):
        await self.fetch_historical_candles()

        try:
            while self.is_running:
                try:
                    data = await asyncio.wait_for(self.ws.recv(), timeout=20.0)
                except asyncio.TimeoutError:
                    print(f"{Fore.YELLOW}Heartbeat timeout. Sending ping...{Style.RESET_ALL}")
                    await self.send({"ping": 1})
                    continue

                data = json.loads(data)
                self.logger.info(f"Received: {data}")

                if "error" in data:
                    self.logger.error(f"API Error: {data['error']}")
                    continue

                if "candles" in data:
                    candles = data["candles"]
                    df = pd.DataFrame(candles)
                    # Convert to numeric
                    for col in ['open', 'high', 'low', 'close']:
                        df[col] = pd.to_numeric(df[col])
                    self.candle_data = df
                    await self.subscribe_to_candles()

                elif "ohlc" in data:
                    ohlc = data["ohlc"]
                    # Update the last candle
                    epoch = int(ohlc["open_time"])

                    if not self.candle_data.empty and self.candle_data.iloc[-1]['epoch'] == epoch:
                         self.candle_data.loc[self.candle_data.index[-1], 'close'] = float(ohlc["close"])
                         self.candle_data.loc[self.candle_data.index[-1], 'high'] = float(ohlc["high"])
                         self.candle_data.loc[self.candle_data.index[-1], 'low'] = float(ohlc["low"])
                    else:
                         # New candle
                         new_row = pd.DataFrame([{
                             'epoch': epoch,
                             'open': float(ohlc["open"]),
                             'high': float(ohlc["high"]),
                             'low': float(ohlc["low"]),
                             'close': float(ohlc["close"])
                         }])
                         self.candle_data = pd.concat([self.candle_data, new_row], ignore_index=True)
                         if len(self.candle_data) > 60:
                             self.candle_data = self.candle_data.iloc[1:].reset_index(drop=True)

                    await self.evaluate_strategy()

                elif "proposal_open_contract" in data:
                    contract = data["proposal_open_contract"]
                    if contract.get("is_sold"):
                        await self.handle_contract_close(contract)

        except asyncio.CancelledError:
            pass
        except websockets.exceptions.ConnectionClosed:
            print(f"{Fore.RED}Websocket connection dropped!{Style.RESET_ALL}")
        finally:
            await self.shutdown()

    async def shutdown(self):
        if self.ws:
            await self.ws.close()
        self.print_summary()

    def print_summary(self):
        win_rate = (self.total_wins / self.total_trades * 100) if self.total_trades > 0 else 0
        pl_color = Fore.GREEN if self.session_pl >= 0 else Fore.RED

        print(f"\n{Fore.CYAN}================ SESSION SUMMARY ================{Style.RESET_ALL}")
        print(f"Total Trades : {self.total_trades}")
        print(f"Wins         : {Fore.GREEN}{self.total_wins}{Style.RESET_ALL}")
        print(f"Losses       : {Fore.RED}{self.total_losses}{Style.RESET_ALL}")
        print(f"Win Rate     : {win_rate:.1f}%")
        print(f"Total P/L    : {pl_color}${self.session_pl:.2f}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}================================================={Style.RESET_ALL}")

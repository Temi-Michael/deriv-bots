import asyncio
import json
import logging
import os
import signal
from logging.handlers import RotatingFileHandler
import websockets
from colorama import init, Fore, Style

init(autoreset=True)

class DerivBot:
    def __init__(self, token, app_id, symbol, tick_window, duration, stake, take_profit, max_runs, strategy_mode, use_martingale, martingale_multiplier, max_martingale_level):
        self.token = token
        self.app_id = app_id
        self.symbol = symbol
        self.tick_window = tick_window
        self.duration = duration
        self.initial_stake = round(float(stake), 2)
        self.current_stake = self.initial_stake
        self.take_profit = float(take_profit)
        self.max_runs = int(max_runs)
        self.strategy_mode = int(strategy_mode)
        self.use_martingale = use_martingale
        self.martingale_multiplier = float(martingale_multiplier)
        self.max_martingale_level = int(max_martingale_level)
        self.current_martingale_level = 0

        self.ws_url = f"wss://ws.binaryws.com/websockets/v3?app_id={self.app_id}"
        self.ws = None
        self.pip_size = None

        self.tick_history = []
        self.digit_history = []

        self.is_running = False
        self.run_count = 0
        self.total_wins = 0
        self.total_losses = 0
        self.session_pl = 0.0
        self.current_contract_id = None

        self.setup_logging()

    def setup_logging(self):
        self.logger = logging.getLogger("DerivBot")
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler("deriv_bot.log", maxBytes=5*1024*1024, backupCount=2)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def connect(self):
        self.logger.info("Connecting to Deriv websocket...")
        print(f"{Fore.CYAN}Connecting to Deriv API...{Style.RESET_ALL}")
        self.ws = await websockets.connect(self.ws_url)

        # Authorize
        await self.send({"authorize": self.token})
        auth_response = await self.receive()
        if "error" in auth_response:
            self.logger.error(f"Auth error: {auth_response['error']}")
            print(f"{Fore.RED}Authorization failed: {auth_response['error']['message']}{Style.RESET_ALL}")
            return False

        print(f"{Fore.GREEN}Authorized successfully!{Style.RESET_ALL}")

        # Get active symbols to determine pip size
        await self.send({"active_symbols": "brief", "product_type": "basic"})
        symbols_response = await self.receive()
        if "error" in symbols_response:
             print(f"{Fore.RED}Failed to fetch symbols.{Style.RESET_ALL}")
             return False

        for sym in symbols_response.get("active_symbols", []):
            if sym["symbol"] == self.symbol:
                self.pip_size = sym["pip"]
                break

        if self.pip_size is None:
            print(f"{Fore.RED}Symbol {self.symbol} not found.{Style.RESET_ALL}")
            return False

        # calculate decimal places from pip size (e.g. 0.001 -> 3)
        # handle scientific notation for tiny pip sizes like 0.00001
        pip_str = f"{self.pip_size:.10f}".rstrip('0').rstrip('.')
        self.decimal_places = len(pip_str.split('.')[-1]) if '.' in pip_str else 0
        print(f"{Fore.CYAN}Determined pip size: {self.pip_size} ({self.decimal_places} decimal places){Style.RESET_ALL}")

        self.is_running = True
        return True

    async def send(self, payload):
        await self.ws.send(json.dumps(payload))
        self.logger.info(f"Sent: {payload}")

    async def receive(self):
        res = await self.ws.recv()
        data = json.loads(res)
        self.logger.info(f"Received: {data}")
        return data

    def extract_last_digit(self, price):
        formatted_price = f"{float(price):.{self.decimal_places}f}"
        return int(formatted_price[-1])

    async def main_loop(self):
        # Subscribe to ticks
        await self.send({"ticks_history": self.symbol, "end": "latest", "count": self.tick_window, "subscribe": 1})

        try:
            while self.is_running:
                data = await self.receive()

                if "error" in data:
                    print(f"{Fore.RED}API Error: {data['error']['message']}{Style.RESET_ALL}")
                    continue

                if "history" in data:
                    # Initial history load
                    prices = data["history"]["prices"]
                    for p in prices:
                        self.tick_history.append(float(p))
                        self.digit_history.append(self.extract_last_digit(p))

                elif "tick" in data:
                    price = float(data["tick"]["quote"])
                    digit = self.extract_last_digit(price)

                    self.tick_history.append(price)
                    self.digit_history.append(digit)

                    if len(self.tick_history) > self.tick_window:
                        self.tick_history.pop(0)
                        self.digit_history.pop(0)

                    # If we don't have an open contract, check for signals
                    if self.current_contract_id is None:
                        await self.evaluate_strategy()

                elif "proposal_open_contract" in data:
                    contract = data["proposal_open_contract"]
                    if contract.get("is_sold"):
                        await self.handle_contract_close(contract)

        except asyncio.CancelledError:
            self.logger.info("Main loop cancelled.")
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("Websocket connection closed unexpectedly.")
        finally:
            await self.shutdown()

    async def evaluate_strategy(self):
        if len(self.digit_history) < self.tick_window:
            return

        signal = None # "OVER" or "UNDER"
        prediction = None

        if self.strategy_mode == 1:
            # Auto Median
            median = sorted(self.digit_history)[len(self.digit_history)//2]
            if median > 4.5:
                signal = "OVER"
                prediction = 3
            elif median < 4.5:
                signal = "UNDER"
                prediction = 6

        elif self.strategy_mode == 2:
            # Strict Over 3 (streak of 3 digits <= 3)
            # Example interpretation: wait for 3 low digits (<= 3)
            if len(self.digit_history) >= 3:
                last_3 = self.digit_history[-3:]
                if all(d <= 3 for d in last_3):
                    signal = "OVER"
                    prediction = 3
                else:
                    print(".", end="", flush=True) # Heartbeat

        elif self.strategy_mode == 3:
            # Strict Under 6 (streak of 3 digits >= 6)
            if len(self.digit_history) >= 3:
                last_3 = self.digit_history[-3:]
                if all(d >= 6 for d in last_3):
                    signal = "UNDER"
                    prediction = 6
                else:
                    print(".", end="", flush=True) # Heartbeat

        if signal:
            if self.strategy_mode in [2, 3]:
                print() # newline after heartbeats
            await self.place_trade(signal, prediction)

    async def place_trade(self, signal_type, prediction):
        contract_type = "DIGITOVER" if signal_type == "OVER" else "DIGITUNDER"

        print(f"\n{Fore.YELLOW}Placing Trade: {contract_type} {prediction} | Stake: ${self.current_stake}{Style.RESET_ALL}")

        trade_req = {
            "buy": 1,
            "price": self.current_stake,
            "parameters": {
                "amount": self.current_stake,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": self.duration,
                "duration_unit": "t",
                "symbol": self.symbol,
                "barrier": str(prediction)
            }
        }

        await self.send(trade_req)
        response = await self.receive()

        if "error" in response:
            print(f"{Fore.RED}Trade Error: {response['error']['message']}{Style.RESET_ALL}")
            return

        buy_info = response.get("buy")
        if buy_info:
            self.current_contract_id = buy_info["contract_id"]
            # Subscribe to the contract
            await self.send({"proposal_open_contract": 1, "contract_id": self.current_contract_id, "subscribe": 1})

    async def handle_contract_close(self, contract):
        profit = float(contract["profit"])
        status = contract["status"]

        if profit > 0:
            print(f"{Fore.GREEN}[WIN] Profit: +${profit:.2f}{Style.RESET_ALL}")
            self.total_wins += 1
            if self.use_martingale:
                self.current_stake = self.initial_stake
                self.current_martingale_level = 0
        else:
            print(f"{Fore.RED}[LOSS] Loss: ${profit:.2f}{Style.RESET_ALL}")
            self.total_losses += 1
            if self.use_martingale:
                if self.current_martingale_level < self.max_martingale_level:
                    self.current_martingale_level += 1
                    self.current_stake = round(self.current_stake * self.martingale_multiplier, 2)
                    print(f"{Fore.MAGENTA}Martingale Level {self.current_martingale_level} - Next Stake: ${self.current_stake}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Max Martingale Level Reached. Resetting Stake.{Style.RESET_ALL}")
                    self.current_stake = self.initial_stake
                    self.current_martingale_level = 0

        self.session_pl += profit
        self.run_count += 1
        print(f"Session P/L: ${self.session_pl:.2f}")

        self.current_contract_id = None

        # Check limits
        if self.session_pl >= self.take_profit:
            print(f"\n{Fore.GREEN}Take Profit Reached (${self.take_profit})! Stopping bot.{Style.RESET_ALL}")
            self.is_running = False

        if self.max_runs > 0 and self.run_count >= self.max_runs:
            print(f"\n{Fore.YELLOW}Max runs ({self.max_runs}) reached. Stopping bot.{Style.RESET_ALL}")
            self.is_running = False

    async def shutdown(self):
        if self.ws:
            await self.ws.close()
        self.print_summary()

    def print_summary(self):
        print(f"\n{Fore.CYAN}--- SESSION SUMMARY ---{Style.RESET_ALL}")
        print(f"Total Trades: {self.total_wins + self.total_losses}")
        print(f"Wins: {Fore.GREEN}{self.total_wins}{Style.RESET_ALL}")
        print(f"Losses: {Fore.RED}{self.total_losses}{Style.RESET_ALL}")

        pl_color = Fore.GREEN if self.session_pl >= 0 else Fore.RED
        print(f"Session P/L: {pl_color}${self.session_pl:.2f}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-----------------------{Style.RESET_ALL}")

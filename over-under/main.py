import asyncio
import os
import signal
import sys
from dotenv import load_dotenv
from src.deriv_bot import DerivBot

def prompt_user():
    print("=== Deriv Over/Under Bot ===")

    asset_type = input("Asset Type (1: Synthetic, 2: Forex) [1]: ") or "1"

    if asset_type == "1":
        symbol = input("Symbol (e.g. R_100, R_50, 1HZ10V) [R_100]: ") or "R_100"
    else:
        symbol = input("Symbol (e.g. frxEURUSD) [frxEURUSD]: ") or "frxEURUSD"

    tick_window = input("Tick window size (for history/median) [10]: ") or "10"
    duration = input("Trade duration (ticks) [1]: ") or "1"
    stake = input("Initial Stake Amount [$1.00]: ") or "1.0"
    take_profit = input("Target Take Profit ($) [10.0]: ") or "10.0"
    max_runs = input("Number of max runs (0 for continuous) [0]: ") or "0"

    print("\n--- Strategy Modes ---")
    print("1. Auto Median (median > 4.5 -> Over 3; median < 4.5 -> Under 6)")
    print("2. Strict Over 3 (waits for 3 consecutive digits <= 3)")
    print("3. Strict Under 6 (waits for 3 consecutive digits >= 6)")
    strategy_mode = input("Select Strategy Mode (1/2/3) [1]: ") or "1"

    martingale_toggle = input("Use Martingale? (y/n) [y]: ").lower() or "y"
    use_martingale = martingale_toggle == 'y'

    if use_martingale:
        martingale_multiplier = input("Martingale Multiplier [2.5]: ") or "2.5"
        max_martingale_level = input("Max Martingale Level [3]: ") or "3"
    else:
        martingale_multiplier = "1.0"
        max_martingale_level = "0"

    return {
        "symbol": symbol,
        "tick_window": int(tick_window),
        "duration": int(duration),
        "stake": stake,
        "take_profit": take_profit,
        "max_runs": max_runs,
        "strategy_mode": strategy_mode,
        "use_martingale": use_martingale,
        "martingale_multiplier": martingale_multiplier,
        "max_martingale_level": max_martingale_level
    }

async def run_bot():
    load_dotenv()
    token = os.getenv("DERIV_API_TOKEN")
    app_id = os.getenv("DERIV_APP_ID", "1089")

    if not token or token == "your_token_here":
        print("Error: Please set DERIV_API_TOKEN in your .env file.")
        return

    config = prompt_user()

    bot = DerivBot(
        token=token,
        app_id=app_id,
        symbol=config["symbol"],
        tick_window=config["tick_window"],
        duration=config["duration"],
        stake=config["stake"],
        take_profit=config["take_profit"],
        max_runs=config["max_runs"],
        strategy_mode=config["strategy_mode"],
        use_martingale=config["use_martingale"],
        martingale_multiplier=config["martingale_multiplier"],
        max_martingale_level=config["max_martingale_level"]
    )

    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\nStopping bot gracefully...")
        bot.is_running = False
        # Cancel the main task if possible, otherwise it will exit loop naturally

    signal.signal(signal.SIGINT, signal_handler)

    if await bot.connect():
        try:
            await bot.main_loop()
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass # Caught gracefully

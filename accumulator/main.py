import asyncio
import os
import signal
import questionary
from dotenv import load_dotenv
from src.bot import AccumulatorBot

async def main():
    load_dotenv(dotenv_path="../.env") # Load from root

    token = os.getenv("DERIV_API_TOKEN")
    app_id = os.getenv("DERIV_APP_ID", "1089")

    if not token or token == "your_token_here":
        print("Error: Please set DERIV_API_TOKEN in the root .env file.")
        return

    print("\n--- Accumulator Trading Bot (Low-Volatility ADX Strategy) ---")

    symbol = questionary.text("Symbol (e.g. R_100, 1HZ100V):", default="R_100").ask()
    growth_rate = questionary.select(
        "Growth Rate:",
        choices=[
            questionary.Choice("1%", '0.01'),
            questionary.Choice("2%", '0.02'),
            questionary.Choice("3%", '0.03'),
            questionary.Choice("4%", '0.04'),
            questionary.Choice("5%", '0.05')
        ]
    ).ask()

    tick_exit_count = questionary.text("Tick Exit Count (auto-sell after N ticks):", default="5").ask()

    stake = questionary.text("Initial Stake ($):", default="1.0").ask()
    take_profit = questionary.text("Take Profit ($):", default="10.0").ask()
    stop_loss = questionary.text("Stop Loss ($):", default="10.0").ask()

    use_martingale = questionary.confirm("Use Martingale on loss?", default=True).ask()
    if use_martingale:
        martingale_mult = questionary.text("Martingale Multiplier:", default="2.0").ask()
        max_martingale = questionary.text("Max Martingale Level:", default="3").ask()
    else:
        martingale_mult = "1.0"
        max_martingale = "0"

    bot = AccumulatorBot(
        token=token,
        app_id=app_id,
        symbol=symbol,
        growth_rate=growth_rate,
        stake=stake,
        take_profit=take_profit,
        stop_loss=stop_loss,
        tick_exit_count=tick_exit_count,
        martingale_mult=martingale_mult,
        max_martingale_level=max_martingale
    )

    def signal_handler(sig, frame):
        print("\nStopping bot gracefully...")
        bot.is_running = False

    signal.signal(signal.SIGINT, signal_handler)

    if await bot.connect():
        await bot.main_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

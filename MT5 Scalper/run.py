import argparse
import time
import logging

from src.bot import ScalperBot

def main():
    parser = argparse.ArgumentParser(description="Run the MT5 Scalper Bot")
    parser.add_argument('--mock', action='store_true', help='Run using the mock MT5 environment')
    parser.add_argument('--symbol', type=str, default='EURUSD', help='Symbol to trade')
    parser.add_argument('--lot', type=float, default=0.1, help='Lot size')
    args = parser.parse_args()

    if args.mock:
        from src.mock_mt5 import mock_mt5 as mt5
        logging.info("Using MOCK MT5 environment.")
    else:
        try:
            import MetaTrader5 as mt5
            logging.info("Using REAL MT5 environment.")
        except ImportError:
            logging.error("MetaTrader5 package not found. Use --mock or install it on Windows.")
            return

    bot = ScalperBot(mt5_module=mt5, symbol=args.symbol, lot=args.lot)

    if not bot.start():
        return

    try:
        while True:
            bot.run_cycle()
            time.sleep(60) # Run every minute for M1
    except KeyboardInterrupt:
        logging.info("Stopping bot...")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()

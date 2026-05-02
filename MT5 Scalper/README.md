# MT5 Scalper Bot

This directory contains a basic Python-based Forex scalping bot using the `MetaTrader5` library. The bot operates on a 1-minute (M1) timeframe and uses Exponential Moving Average (EMA), Stochastic Oscillator, and Average True Range (ATR) for trade entries and exits.

## Features
- **Indicators:** EMA, Stochastic, ATR.
- **Timeframe:** M1.
- **Mock Environment:** Includes `mock_mt5.py` for testing and running without the MetaTrader5 terminal or on non-Windows systems.

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Bot

To run the bot in a mock environment:
```bash
python run.py --mock
```

To run the bot connected to a real MT5 terminal (Windows only):
```bash
python run.py
```

## Running Tests

To run the unit tests:
```bash
python -m unittest discover -s src/tests
```

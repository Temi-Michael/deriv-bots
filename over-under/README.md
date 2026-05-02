# Deriv Over/Under Bot

This is a Python-based bot for the Deriv platform that trades Digit Over/Under contracts. It connects to the Deriv API using pure `websockets` for low latency.

## Features
- **Dynamic Pip Size:** Fetches `active_symbols` to determine strictly correct price formatting based on pip size.
- **Three Strategy Modes:**
  1. Auto Median
  2. Strict Over 3
  3. Strict Under 6
- **Risk Management:**
  - Strict Martingale system (with `round(..., 2)` rounding).
  - Compulsory Take Profit system that automatically shuts down when reached.
- **Interactive Terminal:** Prompts for all settings on startup.
- **Graceful Shutdown & Logging:** Logs to rolling files and catches Ctrl+C to print a Session Summary.

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup your Environment Variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your `DERIV_API_TOKEN` and your `DERIV_APP_ID`.

## Running the Bot

```bash
python main.py
```

## Testing

```bash
python -m unittest discover -s src/tests
```

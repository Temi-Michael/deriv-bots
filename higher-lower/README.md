# Deriv Higher/Lower Bot

This is a Mean Reversion Python bot for the Deriv platform that trades Higher/Lower contracts.

## Strategy
- **Indicators:** Bollinger Bands (Period 20, StdDev 2).
- **Timeframe:** Uses 1-minute (M1) historical candles.
- **Entry Logic:**
  - **LOWER:** When the candle high touches or crosses above the Upper Bollinger Band, the bot buys a **LOWER** contract (expecting the price to fall back). A positive barrier offset is applied.
  - **HIGHER:** When the candle low touches or crosses below the Lower Bollinger Band, the bot buys a **HIGHER** contract (expecting the price to bounce back up). A negative barrier offset is applied.

## Setup Instructions

1. **Navigate to this folder:**
   ```bash
   cd higher-lower
   ```

2. **Setup Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Bot

```bash
python main.py
```
Press `Ctrl+C` at any time for a graceful shutdown and session summary.

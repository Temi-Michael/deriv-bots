# Deriv Accumulator Bot

This is a Low-Volatility Compounding Python bot for the Deriv platform that trades Accumulator contracts.

## Strategy
- **Indicators:** ADX (Average Directional Index, period 14).
- **Timeframe:** Uses 1-minute (M1) historical candles.
- **Entry Logic:**
  - Enters an **Accumulator** contract only when the market is ranging/quiet (ADX < 20).
- **Exit Logic:**
  - Auto-Exit: The bot will track the ticks and actively sell (cash out) the contract when the number of open ticks reaches the user-defined `Tick Exit Count`.

## Setup Instructions

1. **Navigate to this folder:**
   ```bash
   cd accumulator
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

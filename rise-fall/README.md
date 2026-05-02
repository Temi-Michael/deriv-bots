# Deriv Rise/Fall Bot

This is a Trend-following Python bot for the Deriv platform that trades Rise/Fall (CALL/PUT) contracts.

## Strategy
- **Indicators:** Exponential Moving Averages (EMA 8 & EMA 21) and Relative Strength Index (RSI 14).
- **Timeframe:** Uses 1-minute (M1) historical candles for accurate technical analysis.
- **Entry Logic:**
  - **CALL (Rise):** EMA 8 crosses above EMA 21 **AND** RSI > 55.
  - **PUT (Fall):** EMA 8 crosses below EMA 21 **AND** RSI < 45.

## Features
- **Strict Execution:** Uses `asyncio` and `websockets` for rapid execution.
- **Risk Management:** Take Profit, Stop Loss, and Martingale (with absolute safety limits).
- **Interactive CLI:** Prompts you for all necessary settings on startup.

## Setup Instructions

1. **Navigate to this folder:**
   ```bash
   cd rise-fall
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

4. **Environment Variables:**
   Make sure you have your `.env` file configured in the **root** of the monorepo, containing your `DERIV_API_TOKEN`.

## Running the Bot

```bash
python main.py
```
Press `Ctrl+C` at any time for a graceful shutdown and session summary.

## Testing
```bash
python -m unittest discover -s src/tests
```

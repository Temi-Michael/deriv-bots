# Trading Bots Monorepo

Welcome to the **Master Trader** Monorepo! This repository is an advanced, organized collection of isolated algorithmic trading bots. Each bot lives in its own dedicated directory, managing its own code, execution logic, and dependencies independently to ensure maximum safety and modularity.

## Available Bots

Currently, this repository contains **Five (5)** active bots:

### Deriv Platform Bots (WebSockets)
1. **[Rise/Fall Bot (`rise-fall/`)](./rise-fall/README.md)**: Trend-following strategy using EMA (8 & 21) and RSI (14) to catch momentum breakouts.
2. **[Higher/Lower Bot (`higher-lower/`)](./higher-lower/README.md)**: Mean-reversion strategy trading off Bollinger Band touches with custom Barrier Offsets.
3. **[Accumulator Bot (`accumulator/`)](./accumulator/README.md)**: Low-volatility compounding strategy entering only when the ADX indicator signals a ranging market (< 20).
4. **[Over/Under Bot (`over-under/`)](./over-under/README.md)**: Trades Last Digit Prediction (LDP) statistics using Auto-Median or Strict streak logic.

### MetaTrader 5 Bots
5. **[MT5 Scalper (`MT5 Scalper/`)](./MT5%20Scalper/README.md)**: A Python-based Forex scalping bot using the MetaTrader5 terminal on Windows (includes mock environment for testing).

---

## ⚙️ Global Architecture & Standards

- **Environment Secrets:** All Deriv bots pull your secure credentials from a single `.env` file located at the **root** of this repository. **Do not** commit your API tokens to GitHub.
- **Latency:** All Deriv bots utilize raw `asyncio` and `websockets` connections to the Deriv API to ensure execution times are as close to zero as mathematically possible.
- **Precision:** Deriv bots dynamically fetch asset `pip_size` on startup to perfectly format barrier requests, preventing "Invalid Price" API rejections. Stake amounts are strictly rounded to 2 decimal places to maintain valid USD floating point requirements during Martingale expansions.
- **Interactive:** You never need to hard-code variables. All bots launch a beautiful, interactive CLI (`questionary` or `input()`) asking you for your specific trading parameters on startup.
- **Safety Over Everything:**
  - Bots catch `Ctrl+C` for graceful shutdowns.
  - They print a final Session Summary P/L table on exit.
  - Active Take-Profits and Stop-Loss boundaries auto-terminate the bot to secure your capital.

---

## 🚀 General Navigation & Usage

Because this is a monorepo, **you must always navigate into the specific bot's folder before running any commands**.

### Step 1: Set up your global credentials
1. In the root of this repository, copy the example environment file:
   ```bash
   cp over-under/.env.example .env
   ```
2. Open the new `.env` file and insert your `DERIV_API_TOKEN`.

### Step 2: Open your terminal and navigate to the bot you want
```bash
cd rise-fall
```

### Step 3: Set up the bot and run it
Each bot folder has its own `requirements.txt`. Set up a virtual environment and install the dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the interactive terminal:
```bash
python main.py
```

### Step 4: Follow the bot's specific README for more details
- [View Rise/Fall Instructions](./rise-fall/README.md)
- [View Higher/Lower Instructions](./higher-lower/README.md)
- [View Accumulator Instructions](./accumulator/README.md)
- [View Over/Under Instructions](./over-under/README.md)
- [View MT5 Scalper Instructions](./MT5%20Scalper/README.md)

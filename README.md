# Trading Bots Monorepo

Welcome to the Trading Bots Monorepo! This repository is designed to host multiple, isolated trading bots in a single location. Each bot lives in its own dedicated top-level directory and manages its own dependencies, code, and execution logic independently.

## Available Bots

Currently, this repository contains the following bots:

1. **[Deriv Over/Under Bot (`over-under/`)](./over-under/README.md)**: A Python-based bot connecting to the Deriv platform via WebSockets to trade Digit Over/Under contracts.
2. **[MT5 Scalper (`MT5 Scalper/`)](./MT5%20Scalper/README.md)**: A Python-based Forex scalping bot using the MetaTrader5 library (EMA, Stochastic, ATR).

---

## 🚀 General Navigation & Usage

Because this is a monorepo, **you should always navigate into the specific bot's folder before running any commands** (like installing dependencies or running the bot).

Here is the general workflow:

### Step 1: Open your terminal
Open your terminal (Command Prompt, PowerShell, Terminal, etc.) in the root directory of this repository.

### Step 2: Navigate to the bot you want to run
Change your directory into the folder of the bot you wish to use.

For example, to use the Deriv bot:
```bash
cd over-under
```
*(Or `cd "MT5 Scalper"` for the MT5 bot).*

### Step 3: Follow the bot's specific instructions
Once inside the bot's directory, refer to that specific bot's `README.md` file for step-by-step instructions on setting it up and running it.

- [View Deriv Bot Instructions](./over-under/README.md)
- [View MT5 Scalper Instructions](./MT5%20Scalper/README.md)

# MT5 Scalper Bot

This directory contains a Python-based Forex scalping bot using the `MetaTrader5` library. The bot operates on a 1-minute (M1) timeframe and uses Exponential Moving Average (EMA), Stochastic Oscillator, and Average True Range (ATR) for trade entries and exits.

## Features
- **Indicators:** EMA, Stochastic, ATR.
- **Timeframe:** M1.
- **Mock Environment:** Includes a mock testing environment for running the bot without the MetaTrader5 terminal or on non-Windows systems (like Mac/Linux).

---

## 🛠️ Setup Instructions

To run this bot, follow these steps exactly. Make sure you have Python installed on your system.

### Step 1: Navigate to this folder
If you are currently at the root of the repository, you must first change into this bot's specific folder.
```bash
cd "MT5 Scalper"
```

### Step 2: Create a Virtual Environment (Highly Recommended)
It is best practice to create an isolated Python environment for this bot to prevent dependency conflicts.
```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment
Activate the environment you just created. The command differs based on your operating system:

**On Mac/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```cmd
venv\Scripts\activate
```

### Step 4: Install Dependencies
With your virtual environment active, install the required packages:
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Bot

**Important:** Make sure you are inside the `MT5 Scalper` folder and your virtual environment is active.

### Option A: Run in Mock Mode (For Testing / Mac / Linux)
If you do not have MetaTrader5 installed (or are not on Windows), you can run the bot in a simulated mock environment to see how it operates:
```bash
python run.py --mock
```

### Option B: Run in Live Mode (Windows Only)
If you are on Windows and have the MetaTrader5 terminal installed and logged into an account:
```bash
python run.py
```

*Note: You can pass arguments to customize the bot:*
```bash
# Example: Trade GBPUSD with 0.5 lot size
python run.py --symbol GBPUSD --lot 0.5
```

---

## 🧪 Running Tests

To verify that the bot's logic is functioning correctly, you can run the automated test suite.

Ensure you are in the `MT5 Scalper` directory, and run:
```bash
python -m unittest discover -s src/tests
```
You should see output indicating that all tests have passed.

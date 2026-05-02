# Deriv Over/Under Bot

This is a high-speed Python bot for the Deriv platform that trades Digit Over/Under contracts. It connects to the Deriv API using pure `websockets` for the lowest possible latency.

## Features
- **Dynamic Pip Size Check:** Automatically fetches active symbols to strictly format prices and avoid floating-point errors.
- **Three Strategy Modes:** Auto Median, Strict Over 3, and Strict Under 6.
- **Risk Management:** Incorporates a Strict Martingale system (with robust rounding) and a compulsory Take Profit limit.
- **Interactive Terminal:** Prompts for all required settings on startup.
- **Graceful Shutdown & Logging:** Logs data to rolling files and catches `Ctrl+C` to cleanly print a Session Summary.

---

## 🛠️ Setup Instructions

To run this bot, follow these steps exactly. Make sure you have Python installed on your system.

### Step 1: Navigate to this folder
If you are currently at the root of the repository, you must first change into this bot's specific folder.
```bash
cd over-under
```

### Step 2: Create a Virtual Environment (Highly Recommended)
Create an isolated Python environment for this bot to manage its dependencies safely.
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

### Step 5: Configure your Environment Variables
The bot requires an API Token to connect to your Deriv account.

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   *(On Windows Command Prompt, use `copy .env.example .env`)*

2. Open the newly created `.env` file in a text editor.
3. Replace `your_token_here` with your actual Deriv API token.
4. *(Optional)* Change `DERIV_APP_ID` if you registered your own app, otherwise leave it as `1089`.

---

## 🚀 Running the Bot

**Important:** Make sure you are inside the `over-under` folder and your virtual environment is active.

Start the interactive terminal to run the bot:
```bash
python main.py
```

The terminal will prompt you for your trading parameters (Symbol, Stake, Take Profit, Strategy Mode, etc.). Follow the on-screen instructions! 
To stop the bot gracefully at any time and see a session summary, press `Ctrl+C`.

---

## 🧪 Running Tests

To verify that the bot's core logic and strategies are functioning correctly without risking real money, run the automated test suite.

Ensure you are in the `over-under` directory, and run:
```bash
python -m unittest discover -s src/tests
```
You should see output indicating that all tests have passed.

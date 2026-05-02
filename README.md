# Trading Bots Monorepo

Welcome to the Trading Bots Monorepo! This repository contains isolated trading bots, each residing in its own dedicated directory. The goal is to provide a single, organized location for various trading strategies and platforms.

## Repository Structure

- `over-under/`: A Deriv API bot for trading Digit Over/Under contracts.
- `MT5 Scalper/`: A Python-based Forex scalping bot using the MetaTrader5 library.

Each bot directory contains its own:
- `README.md` with specific documentation and instructions.
- `requirements.txt` for specific dependencies.
- `src/` code directory.
- `run.py` or `main.py` entry point.

## Getting Started

To run a specific bot, navigate into its respective directory and follow the instructions in its `README.md`.

Example:
```bash
cd over-under/
pip install -r requirements.txt
python main.py
```

# Python Strategy Trading Bot

This is a Python-based project designed to program trading strategies that can be structured as a class inside the `strategies` folder.

Based on the strategy implemented, this project allows for both **backtesting** and **live execution** of trades, depending on the configuration parameters and execution intervals.

---

## 📦 Dependencies

### MetaTrader 5 (MT5)

This project uses the **MT5 Python library** to send orders to a MetaTrader 5 terminal via a middleware module: `MT5Client.py`.  
Through this class, we can also retrieve data from MT5 to perform **live backtesting** on the implemented strategies.

### Telegram

We use the **Telegram API** to notify events such as:
- Bot startup
- Executed or closed orders

Future plans include adding commands to:
- Check account balance
- Retrieve important trading statistics

### Calendar News (ForexFactory)

Some high-impact news can affect strategy performance.  
To address this, we implemented a **web scraper** that pulls economic news and results from **ForexFactory**.  
This allows the system to make informed decisions based on market events.

---

## ⚙️ Usage

### Backtesting

Backtesting can be performed using:
- Historical data pulled from MT5
- CSV data files

Under the `utils` folder, you will find important modules and helper functions for processing and re-evaluating the data.

### Adding a New Strategy

To add a new strategy:
1. Create a new class in the `strategies` folder.
2. Use either `BackTrader.py` or `LiveTrader.py` to:
   - Load the strategy
   - Evaluate its performance
   - Run it in live trading mode

Remember run the strategy on `BackTrader.py`

---

## 🚧 Challenges

Running strategies across **multiple MT5 accounts** has been a challenge, as MT5 only supports **one active session at a time**.

To overcome this:
- We created a `libs` module
- This module utilizes **Python multithreading**
- Allows multiple MT5 terminals and instances to run simultaneously

---

## 📁 Folder Structure (Simplified)

```
project-root/
│
├── strategies/         # Your custom trading strategies go here
├── utils/              # Data processing and helper tools
├── libs/               # Multithreading tools for multiple MT5 instances
├── MT5Client.py        # MT5 middleware
├── BackTrader.py       # Module for backtesting strategies
├── LiveTrader.py       # Module for live trading
```

---

## 📬 Contributions

Feel free to fork, contribute, or suggest new features and improvements!

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

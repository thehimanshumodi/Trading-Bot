# Simplified Binance Futures Trading Bot (Testnet)

This project provides a basic Python-based trading bot designed to interact with the Binance Futures Testnet. It demonstrates how to place market, limit, and stop-limit orders, handle user input via the command line, and implement robust logging and error handling for API interactions.

This bot is ideal for technical assessments or for those looking to understand the fundamentals of algorithmic trading on Binance Futures in a simulated environment.

## Features

* **Order Placement:** Supports `MARKET`, `LIMIT`, and `STOP-LIMIT` (futures `STOP`) order types.
* **Order Sides:** Supports both `BUY` and `SELL` order sides.
* **Binance Futures Testnet:** Configured to interact with the Binance Futures Testnet API (`https://testnet.binancefuture.com`), ensuring no real funds are risked.
* **Command-Line Interface (CLI):** Simple, interactive CLI for accepting user input for order parameters.
* **Comprehensive Logging:** Detailed logging of API requests, responses, and errors to the console, aiding in debugging and monitoring.
* **Robust Error Handling:** Catches and reports specific Binance API errors (`BinanceAPIException`) and request-related issues (`BinanceRequestException`).
* **Input Validation:** Ensures user-provided quantities and prices are valid numeric values.

## Prerequisites

Before running the bot, ensure you have the following:

* **Python 3.x:** Installed on your system.
* **`python-binance` library:** This official Binance API wrapper for Python is required. Install it using pip:
    ```bash
    pip install python-binance
    ```
* **Binance Futures Testnet Account:**
    * Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com) to register and log in.
    * Generate **API Key** and **API Secret** from the API Management section on the Testnet site. Ensure these keys have permissions for Futures trading.

## Installation

1.  **Clone the repository (or save the script):**
    If you received this as a script, simply save it as `trading_bot.py`.
    (If this were a full repository, you'd clone it: `git clone <repo-url>`)

2.  **Install dependencies:**
    ```bash
    pip install python-binance
    ```

## Usage

1.  **Run the script from your terminal:**
    Navigate to the directory where you saved `trading_bot.py` and execute:
    ```bash
    python trading_bot.py
    ```

2.  **Provide API Credentials:**
    The bot will prompt you to enter your Binance Testnet API Key and API Secret.
    * **Security Note:** For enhanced security, you can set your API Key and Secret as environment variables (`BINANCE_API_KEY` and `BINANCE_API_SECRET`). The bot will automatically use them if found.
        * **Linux/macOS:**
            ```bash
            export BINANCE_API_KEY="YOUR_API_KEY"
            export BINANCE_API_SECRET="YOUR_API_SECRET"
            ```
        * **Windows (Command Prompt):**
            ```cmd
            set BINANCE_API_KEY="YOUR_API_KEY"
            set BINANCE_API_SECRET="YOUR_API_SECRET"
            ```
        * **Windows (PowerShell):**
            ```powershell
            $env:BINANCE_API_KEY="YOUR_API_KEY"
            $env:BINANCE_API_SECRET="YOUR_API_SECRET"
            ```

3.  **Interact with the CLI:**
    Follow the on-screen menu to choose an order type (Market, Limit, Stop-Limit) and provide the necessary parameters (symbol, side, quantity, price, stop price, etc.).

    Example Interaction:
    ```
    --- Binance Futures Testnet Trading Bot ---
    ... (API key/secret prompts) ...

    --- Place a New Order ---
    1. Market Order
    2. Limit Order
    3. Stop-Limit Order (Bonus)
    4. Exit
    Enter order type (1-4): 2
    Enter trading pair (e.g., BTCUSDT): BTCUSDT
    Enter order side (BUY/SELL): BUY
    Enter quantity: 0.001
    Enter limit price: 30000
    Enter TimeInForce (GTC/IOC/FOK, default GTC): GTC
    ```

## Order Types Supported

* **Market Order:**
    * `symbol`: Trading pair (e.g., `BTCUSDT`)
    * `side`: `BUY` or `SELL`
    * `quantity`: Amount of base asset (e.g., BTC for BTCUSDT)
* **Limit Order:**
    * `symbol`: Trading pair
    * `side`: `BUY` or `SELL`
    * `quantity`: Amount of base asset
    * `price`: Desired execution price
    * `timeInForce`: (`GTC`, `IOC`, `FOK` - default `GTC`)
* **Stop-Limit Order (Futures `STOP` Order):**
    * `symbol`: Trading pair
    * `side`: `BUY` or `SELL`
    * `quantity`: Amount of base asset
    * `price`: The limit price at which the order should be executed once `stopPrice` is hit.
    * `stopPrice`: The price at which the stop order becomes active.
    * `timeInForce`: (`GTC`, `IOC`, `FOK` - default `GTC`)

## Error Handling & Logging

The bot includes robust error handling to catch common API issues and network problems. All API requests, responses, and errors are logged to the console using Python's `logging` module. This provides clear visibility into the bot's operations and helps in diagnosing issues.

## Important Notes

* **Testnet Only:** This bot is designed exclusively for the Binance Futures Testnet. **DO NOT use your live API keys with this script, as it can lead to real financial losses.**
* **Trading Rules:** Be aware of the minimum order sizes, price precision, and quantity precision for each trading pair on Binance Futures. API errors like "filter_price" or "filter_lot_size" indicate that your order parameters do not adhere to these rules. You can query `client.futures_exchange_info()` to get these details for specific symbols.
* **Disclaimer:** This is a simplified example for educational and demonstrative purposes. It does not include advanced features like portfolio management, risk management, real-time data analysis, or complex trading strategies. Use at your own risk.

---

**Contributions & Feedback:**
Feel free to provide feedback or suggest improvements for this simplified bot!

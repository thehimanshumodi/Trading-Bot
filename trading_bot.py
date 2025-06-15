import logging
import sys
import os
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Configure logging
# Create a logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set the logging level to INFO

# Create a console handler and set its format
console_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Optional: Create a file handler to log to a file
# file_handler = logging.FileHandler('trading_bot.log')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

class BasicBot:
    """
    A simplified trading bot for Binance Futures Testnet.
    Supports placing market, limit, and stop-limit orders.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initializes the Binance client with provided API credentials.

        Args:
            api_key (str): Your Binance API key.
            api_secret (str): Your Binance API secret.
            testnet (bool): If True, uses the Binance Futures Testnet URL.
                            Defaults to True.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet

        # Binance Futures Testnet base URL
        self.base_url = "https://testnet.binancefuture.com"

        try:
            # Initialize the Binance client without base_url parameter
            self.client = Client(api_key, api_secret)
            # Override the API URL for testnet
            self.client.API_URL = self.base_url
            logger.info(f"Binance client initialized. Testnet mode: {self.testnet}")
            # Verify connectivity (optional, but good for initial setup)
            self.client.futures_ping()
            logger.info("Successfully connected to Binance Futures API.")
        except BinanceRequestException as e:
            logger.error(f"Failed to connect to Binance Futures API: {e}")
            logger.error("Please check your internet connection or API endpoint.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"An unexpected error occurred during client initialization: {e}")
            sys.exit(1)

    def _send_order_request(self, order_func, **kwargs) -> dict | None:
        """
        Centralized function to send order requests, handle responses, and log.

        Args:
            order_func (callable): The Binance client method to call (e.g., self.client.futures_create_order).
            **kwargs: Keyword arguments to pass to the order_func.

        Returns:
            dict | None: The order response dictionary if successful, None otherwise.
        """
        order_type = kwargs.get('type', 'UNKNOWN')
        symbol = kwargs.get('symbol', 'UNKNOWN')
        side = kwargs.get('side', 'UNKNOWN')

        logger.info(f"Attempting to place a {order_type} order for {symbol} ({side})...")
        logger.debug(f"Request parameters: {kwargs}")

        try:
            response = order_func(**kwargs)
            logger.info(f"Order placed successfully! Type: {order_type}, Symbol: {symbol}, Side: {side}")
            logger.info(f"API Response: {response}")
            return response
        except BinanceAPIException as e:
            logger.error(f"Binance API Error for {order_type} order ({symbol}, {side}):")
            logger.error(f"  Code: {e.code}, Message: {e.message}")
            if e.message.lower().find("margin is insufficient") != -1:
                logger.error("  Action Required: Insufficient margin. Please deposit funds or reduce order size.")
            elif e.message.lower().find("filter_price") != -1 or e.message.lower().find("filter_lot_size") != -1:
                logger.error("  Action Required: Price or quantity not adhering to symbol's trading rules (e.g., step size, min/max).")
            return None
        except BinanceRequestException as e:
            logger.error(f"Binance Request Error for {order_type} order ({symbol}, {side}):")
            logger.error(f"  Reason: {str(e)}")
            logger.error("  Action Required: Network issue or invalid request format. Check your internet or parameters.")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while placing {order_type} order ({symbol}, {side}): {e}")
            return None

    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict | None:
        """
        Places a market order on Binance Futures.

        Args:
            symbol (str): The trading pair (e.g., 'BTCUSDT').
            side (str): 'BUY' or 'SELL'.
            quantity (float): The amount of base asset to trade.

        Returns:
            dict | None: The order response if successful, None otherwise.
        """
        if quantity <= 0:
            logger.warning("Market order quantity must be greater than 0.")
            return None

        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': quantity
        }
        return self._send_order_request(self.client.futures_create_order, **params)

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, time_in_force: str = 'GTC') -> dict | None:
        """
        Places a limit order on Binance Futures.

        Args:
            symbol (str): The trading pair (e.g., 'BTCUSDT').
            side (str): 'BUY' or 'SELL'.
            quantity (float): The amount of base asset to trade.
            price (float): The price at which the order should be executed.
            time_in_force (str): 'GTC' (Good Till Cancel) or 'IOC' (Immediate Or Cancel) or 'FOK' (Fill Or Kill).
                                 Defaults to 'GTC'.

        Returns:
            dict | None: The order response if successful, None otherwise.
        """
        if quantity <= 0 or price <= 0:
            logger.warning("Limit order quantity and price must be greater than 0.")
            return None

        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'LIMIT',
            'quantity': quantity,
            'price': f'{price:.8f}', # Format price to 8 decimal places for precision
            'timeInForce': time_in_force.upper()
        }
        return self._send_order_request(self.client.futures_create_order, **params)

    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, price: float, stop_price: float, time_in_force: str = 'GTC') -> dict | None:
        """
        Places a stop-limit order on Binance Futures.
        This order type involves a 'stopPrice' that, when triggered, places a 'limit' order at 'price'.

        Args:
            symbol (str): The trading pair (e.g., 'BTCUSDT').
            side (str): 'BUY' or 'SELL'.
            quantity (float): The amount of base asset to trade.
            price (float): The limit price at which the order should be executed once the stop_price is hit.
            stop_price (float): The price at which the stop order becomes active.
            time_in_force (str): 'GTC' (Good Till Cancel) or 'IOC' (Immediate Or Cancel) or 'FOK' (Fill Or Kill).
                                 Defaults to 'GTC'.

        Returns:
            dict | None: The order response if successful, None otherwise.
        """
        if quantity <= 0 or price <= 0 or stop_price <= 0:
            logger.warning("Stop-limit order quantity, price, and stop price must be greater than 0.")
            return None

        # For futures, 'STOP' type is used for stop-limit orders.
        # It requires 'price' (limit price) and 'stopPrice'.
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'STOP_MARKET', # Changed to STOP_MARKET for Futures API stop-limit orders
            'quantity': quantity,
            'price': f'{price:.8f}',
            'stopPrice': f'{stop_price:.8f}',
            'timeInForce': time_in_force.upper()
        }
        return self._send_order_request(self.client.futures_create_order, **params)

def validate_numeric_input(prompt: str, value_type: type, min_value: float = 0.0) -> float:
    """
    Validates user input to ensure it's a number and greater than a minimum value.

    Args:
        prompt (str): The message to display to the user.
        value_type (type): The expected type (e.g., float, int).
        min_value (float): The minimum acceptable value.

    Returns:
        float: The validated numeric input.
    """
    while True:
        try:
            value = value_type(input(prompt))
            if value <= min_value:
                logger.warning(f"Input must be greater than {min_value}. Please try again.")
            else:
                return value
        except ValueError:
            logger.warning("Invalid input. Please enter a valid number.")

def get_user_credentials():
    """
    Prompts the user for API key and secret.
    Can also be configured to read from environment variables for security.
    """
    logger.info("\n--- Binance Futures Testnet Trading Bot ---")
    logger.info("Please ensure you have generated API credentials from your Binance Testnet account.")
    logger.info("Visit: https://testnet.binancefuture.com")
    logger.info("For security, consider setting API_KEY and API_SECRET as environment variables.")

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key:
        api_key = input("Enter your Binance Testnet API Key: ").strip()
    else:
        logger.info("Using API Key from environment variable.")

    if not api_secret:
        api_secret = input("Enter your Binance Testnet API Secret: ").strip()
    else:
        logger.info("Using API Secret from environment variable.")

    if not api_key or not api_secret:
        logger.error("API Key and Secret cannot be empty. Exiting.")
        sys.exit(1)

    return api_key, api_secret

def main():
    """
    Main function to run the trading bot's command-line interface.
    """
    api_key, api_secret = get_user_credentials()

    bot = BasicBot(api_key, api_secret, testnet=True)

    while True:
        print("\n--- Place a New Order ---")
        print("1. Market Order")
        print("2. Limit Order")
        print("3. Stop-Limit Order (Bonus)")
        print("4. Exit")

        choice = input("Enter order type (1-4): ").strip()

        if choice == '4':
            logger.info("Exiting trading bot. Goodbye!")
            break

        symbol = input("Enter trading pair (e.g., BTCUSDT): ").strip().upper()
        if not symbol:
            logger.warning("Symbol cannot be empty.")
            continue

        side = input("Enter order side (BUY/SELL): ").strip().upper()
        if side not in ['BUY', 'SELL']:
            logger.warning("Invalid side. Please enter 'BUY' or 'SELL'.")
            continue

        quantity = validate_numeric_input("Enter quantity: ", float)

        order_response = None
        if choice == '1': # Market Order
            order_response = bot.place_market_order(symbol, side, quantity)
        elif choice == '2': # Limit Order
            price = validate_numeric_input("Enter limit price: ", float)
            time_in_force = input("Enter TimeInForce (GTC/IOC/FOK, default GTC): ").strip().upper() or 'GTC'
            if time_in_force not in ['GTC', 'IOC', 'FOK']:
                logger.warning("Invalid TimeInForce. Using GTC.")
                time_in_force = 'GTC'
            order_response = bot.place_limit_order(symbol, side, quantity, price, time_in_force)
        elif choice == '3': # Stop-Limit Order
            price = validate_numeric_input("Enter limit price for stop-limit order: ", float)
            stop_price = validate_numeric_input("Enter stop price: ", float)
            time_in_force = input("Enter TimeInForce (GTC/IOC/FOK, default GTC): ").strip().upper() or 'GTC'
            if time_in_force not in ['GTC', 'IOC', 'FOK']:
                logger.warning("Invalid TimeInForce. Using GTC.")
                time_in_force = 'GTC'
            order_response = bot.place_stop_limit_order(symbol, side, quantity, price, stop_price, time_in_force)
        else:
            logger.warning("Invalid choice. Please select 1, 2, 3, or 4.")
            continue

        if order_response:
            logger.info(f"\nOrder ID: {order_response.get('orderId')}")
            logger.info(f"Client Order ID: {order_response.get('clientOrderId')}")
            logger.info(f"Status: {order_response.get('status')}")
            logger.info(f"Executed Quantity: {order_response.get('executedQty', 'N/A')}")
            logger.info(f"Cum Quote Quantity: {order_response.get('cumQuote', 'N/A')}") # Total spent/received in quote asset
        else:
            logger.error("\nOrder placement failed. See logs above for details.")

if __name__ == "__main__":
    main()

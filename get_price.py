# Get stock price for given ticker

import datetime
import yfinance as yf

def get_stock_price(ticker):
    """A tool that fetches the latest stock price for a given ticker symbol from Yahoo Finance.
    Args:
        ticker: A string representing the stock ticker symbol (e.g., "AAPL" for Apple).
    """



    try:
        # Get the current time in EST (Eastern Time Zone)
        current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6)))

        # Market open and close times (EST)
        market_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = current_time.replace(hour=16, minute=0, second=0, microsecond=0)

        stock = yf.Ticker(ticker)
        price = None
        currency = stock.fast_info.get("currency", "USD")

        # Check if the market is open
        if market_open <= current_time <= market_close:
            # Try to get live price
            price = stock.fast_info.get("last_price")
        else:
            # Market is closed, use last closing price
            hist = stock.history(period="1d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]  # Last closing price

        if price is None:
            return "Price unavailable"

        return f"{currency} {price:,.2f}"

    except Exception as e:
        return f"Error fetching price: {e}"
    

    # Ensure the script still works when run manually
if __name__ == "__main__":
    print(get_stock_price("TSLA"))
# Get stock price for given ticker

from decimal import Decimal
import yfinance as yf
import logging

def get_stock_price(ticker):
    """
    Fetches the latest stock price using Yahoo Finance.
    """
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]  # Get latest closing price
        rounded_price = round(price,2)
        return Decimal(str(rounded_price))  # Convert to Decimal for DynamoDB
    except Exception as e:
        logging.error(f"❌ Error fetching stock price for {ticker}: {e}")
        return None
    
def get_market_cap(ticker):
    """
    Fetches the market capitalization using Yahoo Finance.
    """
    try:
        stock = yf.Ticker(ticker)
        market_cap = stock.info.get("marketCap")  # Get market cap
        
        if market_cap is None:
            logging.warning(f"⚠️ Market cap not found for {ticker}.")
            return None

        return Decimal(str(market_cap))  # Convert to Decimal for DynamoDB
    
    except Exception as e:
        logging.error(f"❌ Error fetching market cap for {ticker}: {e}")
        return None

# Ensure the script still works when run manually
if __name__ == "__main__":
    print(get_stock_price("TSLA"))
    print(get_market_cap("TSLA"))
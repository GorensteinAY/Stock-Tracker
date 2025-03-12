# Update list of companies stored in DynamoDB with latest financials
# Revenue, Net Income, Net Cash taken from SEC EDGAR database
# Stock price, Market cap taken from Yahoo Finance

import boto3
import time
import decimal
import logging
from get_cik import *
from get_financials import get_latest_financials 
from get_price import *
from dynamodb_utils import update_time

# AWS Config
DYNAMODB_TABLE = "StockTickers"

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE)

# Initialize CIK lookup
cik_mapping, name_mapping = load_sec_ticker_data()

def update_financials(ticker):

    try:
        # Look up CIK from ticker
        cik = get_cik_by_ticker(ticker, cik_mapping)

        if not cik:
            logging.info(f"⚠️ No CIK found for ticker {ticker}. Skipping update.")
            return

        # Fetch financials using CIK
        financials = get_latest_financials(cik)
        
        # Convert to Decimal (ensuring negative values are kept)
        financials_cleaned = {
            k: Decimal(str(v)) for k, v in financials.items() if v is not None
        }

        # Log the update
        logging.info(f"🔹 Updating {ticker} (CIK: {cik}) with: {financials_cleaned}")

        # Prepare attribute names and values
        update_expression = "SET " + ", ".join(f"#{k} = :{k}" for k in financials_cleaned)
        expression_attribute_values = {f":{k}": v for k, v in financials_cleaned.items()}
        expression_attribute_names = {f"#{k}": k for k in financials_cleaned}

        # Perform the update
        table.update_item(
            Key={"Ticker": ticker},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names
        )

        logging.info(f"✅ Updated financials for {ticker} (CIK {cik})")
    
    except Exception as e:
        logging.error(f"❌ Error updating financials for {ticker}: {e}")

def update_price(ticker):
    """
    Updates the stock price for a single ticker in DynamoDB.
    """
    price = get_stock_price(ticker)
    
    if price is None:
        logging.info(f"⚠️ Skipping update for {ticker}: No valid price found.")
        return False

    try:
        table.update_item(
            Key={"Ticker": ticker},
            UpdateExpression="SET Stock_Price = :p",
            ExpressionAttributeValues={":p": price},
        )
        logging.info(f"✅ Updated {ticker} with price {price}")
        return True
    except Exception as e:
        logging.error(f"❌ Error updating {ticker} in DynamoDB: {e}")
        return False
    
def update_cap(ticker):
    """
    Updates the stock market capitalization for a single ticker in DynamoDB.
    """
    cap = get_market_cap(ticker)
    
    if cap is None:
        logging.warning(f"⚠️ Skipping update for {ticker}: No valid market cap found.")
        return False

    try:
        table.update_item(
            Key={"Ticker": ticker},
            UpdateExpression="SET Stock_Market_Cap = :c",
            ExpressionAttributeValues={":c": cap},
        )
        logging.info(f"✅ Updated {ticker} with market cap {cap}")
        return True
    except Exception as e:
        logging.error(f"❌ Error updating {ticker} in DynamoDB: {e}")
        return False

def update_ratios(ticker):
    """Fetches financial data, calculates P/E Ratio and Market Cap/Net Cash, then updates DynamoDB."""
    try:
        # Retrieve item from DynamoDB
        response = table.get_item(Key={"Ticker": ticker})
        if "Item" not in response:
            logging.warning(f"⚠️ {ticker} not found in DynamoDB.")
            return

        item = response["Item"]

        # Extract required values
        stock_price = decimal.Decimal(item.get("Stock_Price", 0))
        net_income = decimal.Decimal(item.get("Net_Income", 0))
        market_cap = decimal.Decimal(item.get("Stock_Market_Cap", 0))
        net_cash = decimal.Decimal(item.get("Net_Cash", 0))

        # Avoid division by zero
        pe_ratio = round((market_cap / net_income),2) if net_income else None
        mc_net_cash_ratio = round((market_cap / net_cash),2) if net_cash else None

        # Prepare update expression
        update_expression = "SET Table_PE_Ratio = :pe, Table_MC_Net_Cash_Ratio = :mc"
        expression_values = {
            ":pe": pe_ratio if pe_ratio is not None else decimal.Decimal(0),
            ":mc": mc_net_cash_ratio if mc_net_cash_ratio is not None else decimal.Decimal(0),
        }

        # Update DynamoDB
        table.update_item(
            Key={"Ticker": ticker},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
        )

        logging.info(f"✅ Updated ratios for {ticker}: P/E={pe_ratio}, MC/NetCash={mc_net_cash_ratio}")

    except Exception as e:
        logging.error(f"❌ Error calculating ratios for {ticker}: {e}")



def update_dynamodb():
    # Loop through companies in DynamoDB and update their latest financials.
    
    response = table.scan()
    companies = response.get("Items", [])

    for company in companies:
        update_financials(ticker = company["Ticker"])
        update_cap(ticker = company["Ticker"])
        update_price(ticker = company["Ticker"])
        update_ratios(ticker = company["Ticker"])
        update_time(ticker = company["Ticker"])
        time.sleep(0.1)  # Respect rate limit

"""
# Run manually
if __name__ == "__main__":
    update_dynamodb()
"""
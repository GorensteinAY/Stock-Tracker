import boto3
import logging
from decimal import Decimal
from datetime import datetime
from logger import logger, has_warnings_or_errors
from collections import Counter
from config import DYNAMODB_TABLE_NAME, AWS_REGION

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def insert_ticker(ticker: str):
    """Inserts a stock ticker into the DynamoDB table."""
    response = table.put_item(
        Item={
            'Ticker': ticker
        }
    )
    print(f"Inserted {ticker}: {response}")
    return response

def get_all_tickers():
    """Retrieves all stock tickers from the DynamoDB table."""
    response = table.scan()
    return response.get('Items', [])

def clean_duplicates():
    """Removes duplicate tickers, keeping only the first occurrence."""
    try:
        response = table.scan()
        items = response.get("Items", [])

        if not items:
            logging.info("✅ No items found in DynamoDB.")
            return

        ticker_counts = Counter()
        rows_to_delete = []

        for item in items:
            ticker = item.get("Ticker")
            ticker_counts[ticker] += 1

        for ticker, count in ticker_counts.items():
            if count > 1:
                duplicates = [item for item in items if item["Ticker"] == ticker]
                # Keep the first one, delete the rest
                rows_to_delete.extend([d["Ticker"] for d in duplicates[1:]])

        for ticker in set(rows_to_delete):
            table.delete_item(Key={"Ticker": ticker})
            logging.info(f"🗑️ Deleted duplicate: {ticker}")

        logging.info("✅ Duplicate removal complete.")

    except Exception as e:
        logging.error(f"❌ Error during duplicate clean-up: {e}")

def clean_cik():
    """Removes rows that have no CIK."""
    try:
        response = table.scan()
        items = response.get("Items", [])

        rows_to_delete = [item["Ticker"] for item in items if not item.get("CIK")]

        for ticker in rows_to_delete:
            table.delete_item(Key={"Ticker": ticker})
            logging.info(f"🗑️ Deleted {ticker} due to missing CIK.")

        logging.info("✅ CIK clean-up complete.")

    except Exception as e:
        logging.error(f"❌ Error during CIK clean-up: {e}")

def clean_financials():
    """Removes rows missing key financial data (Price, Market Cap, Revenue, Net Income, Net Cash)."""
    try:
        response = table.scan()
        items = response.get("Items", [])

        required_fields = ["Stock_Price", "Stock_Market_Cap", "Net_Income", "Revenue", "Net_Cash"]
        rows_to_delete = [
            item["Ticker"] for item in items
            if any(item.get(field) is None for field in required_fields)
        ]

        for ticker in rows_to_delete:
            table.delete_item(Key={"Ticker": ticker})
            logging.info(f"🗑️ Deleted {ticker} due to missing financial data.")

        logging.info("✅ Financial clean-up complete.")

    except Exception as e:
        logging.error(f"❌ Error during financial clean-up: {e}")


def delete_column(column):
    """Delete a column from DynamoDB"""

    # Scan the table to get all items
    response = table.scan()
    items = response.get("Items", [])

    # Loop through items and remove the column
    for item in items:
        primary_key = {"Ticker": item["Ticker"]}  # Update this key structure based on your table schema

        # Remove the erroneous column
        table.update_item(
            Key=primary_key,
            UpdateExpression=f"REMOVE {column}"
        )

    print("✅ Deleted {column} from DynamoDB")    

def delete_row(ticker):
    response = table.delete_item(
        Key={"Ticker": ticker}  # Assuming "Ticker" is the primary key
    )
    print(f"✅ Deleted {ticker} from DynamoDB")

def update_time(ticker):
    """Update the last updated timestamp in DynamoDB if no warnings/errors exist for the ticker."""
    if has_warnings_or_errors(ticker):
        logger.warning(f"⏳ Skipping timestamp update for {ticker} due to previous warnings/errors.")
        return

    timestamp = datetime.utcnow().isoformat()
    
    try:
        table.update_item(
            Key={"Ticker": ticker},
            UpdateExpression="SET Updated = :u",
            ExpressionAttributeValues={":u": timestamp},
        )
        logger.info(f"✅ Updated timestamp for {ticker}: {timestamp}")
    except Exception as e:
        logger.error(f"❌ Error updating timestamp for {ticker}: {str(e)}")

""""
# Run manually
if __name__ == "__main__":
    clean_financials()
"""
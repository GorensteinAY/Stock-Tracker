# Update list of companies stored in DynamoDB with latest financials from SEC EDGAR database


import boto3
import time
import logging
from decimal import Decimal
from cik_lookup import *
from get_financials import get_latest_financials 

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
            logging.warning(f"⚠️ No CIK found for ticker {ticker}. Skipping update.")
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

        logging.info(f"✅ Successfully updated financials for {ticker} (CIK {cik})")
        print(f"✅ Updated {ticker}: {financials}")
    
    except Exception as e:
        logging.error(f"❌ Error updating financials for {ticker}: {e}")


def update_dynamodb():
    # Loop through companies in DynamoDB and update their latest financials.
    
    response = table.scan()
    companies = response.get("Items", [])

    for company in companies:
        update_financials(ticker = company["Ticker"])

        time.sleep(1.1)  # Respect SEC rate limit

# Run the update
if __name__ == "__main__":
    update_dynamodb()
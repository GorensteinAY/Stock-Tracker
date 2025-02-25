import boto3
import csv
import logging

# AWS Configuration
AWS_REGION = "us-east-1"  # Change this to your region
DYNAMODB_TABLE_NAME = "StockTickers"  # Change to your actual table name

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

# Function to upload CSV to DynamoDB
def upload_csv_to_dynamodb(csv_file):
    """Uploads data from CSV to DynamoDB, skipping tickers that already exist."""
    try:
        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=";")  # Adjust delimiter if needed
            
            for row in reader:
                ticker = row.get("Ticker")
                cik = row.get("CIK")

                if not ticker or not cik:
                    logging.warning(f"⚠️ Skipping row due to missing data: {row}")
                    continue

                # Check if ticker already exists in DynamoDB
                response = table.get_item(Key={"Ticker": ticker})
                if "Item" in response:
                    logging.info(f"🔄 Skipping {ticker} (already in DynamoDB)")
                    continue

                # Add to DynamoDB
                table.put_item(Item={"Ticker": ticker, "CIK": cik})
                logging.info(f"✅ Added {ticker} to DynamoDB.")

        logging.info("🎯 CSV upload complete.")

    except Exception as e:
        logging.error(f"❌ Error processing CSV: {e}")

# Example usage
upload_csv_to_dynamodb("Updated_Tickers.csv")
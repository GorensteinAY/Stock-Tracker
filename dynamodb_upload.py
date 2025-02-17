import boto3
import pandas as pd
from decimal import Decimal, InvalidOperation

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
table_name = "StockTickers"  # Replace with your actual table name
table = dynamodb.Table(table_name)

# Load CSV data (with semicolon delimiter)
csv_file = "tickers.csv"  # Ensure this is in the same directory
df = pd.read_csv(csv_file, delimiter=';')

# Clean the column names (strip any spaces)
df.columns = df.columns.str.strip()

# Insert each row into DynamoDB
def upload_tickers():
    for _, row in df.iterrows():
        # Ensure the company name is a string (even if it's a float, NaN, etc.)
        company_name = str(row["CompanyName"]).title()  # Convert to string and capitalize each word
        
        # Check if ticker contains only letters (alphabetic characters)
        ticker = row["Ticker"]
        if not ticker.isalpha():
            print(f"❌ Invalid Ticker (not alphabetic): {ticker}, skipping...")
            continue  # Skip this row if ticker is not alphabetic

        try:
            # Ensure ticker is treated as a string (not as a Decimal)
            ticker = str(ticker).upper()  # Store ticker as a string and convert to uppercase

        except InvalidOperation:
            print(f"❌ Invalid Ticker: {ticker}, skipping...")
            continue  # Skip this row if ticker is invalid
        
        # Check if the ticker already exists in the table
        response = table.get_item(
            Key={
                'Ticker': ticker  # Check for existing Ticker
            }
        )

        # If the ticker already exists, skip this insert
        if 'Item' in response:
            print(f"✅ Ticker {ticker} already exists. Skipping insert.")
            continue

        # Insert into DynamoDB only if the ticker does not exist
        response = table.put_item(
            Item={
                "Ticker": ticker,  # Ticker is stored as a string
                "CompanyName": company_name
            }
        )
        print(f"Uploaded: {ticker} - {company_name}")

    print("✅ Upload complete!")

# Run the function
if __name__ == "__main__":
    upload_tickers()

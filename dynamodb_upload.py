import boto3
import csv
import time
from decimal import Decimal

# AWS Configuration
AWS_REGION = "us-east-1"  # Change this to your region
DYNAMODB_TABLE_NAME = "StockTickers"  # Change to your actual table name

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

# Function to upload CSV to DynamoDB
def upload_csv_to_dynamodb(csv_file):
    with open(csv_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")  # Ensure delimiter is correct
        total_uploaded = 0

        for row in reader:
            try:
                # Convert CIK to a string, ensuring no float conversion issues
                cik = str(row["CIK"]).strip() if row.get("CIK") else None
                ticker = row["Ticker"].strip().upper() if row.get("Ticker") else None
                company_name = row["CompanyName"].strip() if row.get("CompanyName") else None

                if not ticker or not cik:
                    print(f"Skipping row: Missing Ticker or CIK → {row}")
                    continue  # Skip rows without essential data

                # Insert into DynamoDB
                table.put_item(
                    Item={
                        "Ticker": ticker,
                        "CIK": cik,
                        "CompanyName": company_name,
                    }
                )

                total_uploaded += 1
                print(f"✅ Uploaded {ticker} | CIK: {cik}")

                time.sleep(0.1)  # Optional: Throttle requests to prevent overload

            except Exception as e:
                print(f"❌ Error uploading row {row}: {e}")

    print(f"✅ Upload complete: {total_uploaded} records added to DynamoDB.")

# Run the function
csv_filename = "Updated_Tickers.csv"  # Update with your actual CSV filename
upload_csv_to_dynamodb(csv_filename)

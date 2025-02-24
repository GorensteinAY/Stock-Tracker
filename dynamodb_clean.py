# Clean DynamoDB

import boto3

# AWS Configuration
AWS_REGION = "us-east-1"  # Change this if needed
DYNAMODB_TABLE_NAME = "StockTickers"

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

# Scan the table and delete items where 'CIK' is missing or empty
def clean_dynamodb():
    response = table.scan()
    items = response.get("Items", [])

    deleted_count = 0

    for item in items:
        if "CIK" not in item or not item["CIK"]:  # Check if CIK is missing or empty
            ticker = item["Ticker"]
            table.delete_item(Key={"Ticker": ticker})
            deleted_count += 1
            print(f"🗑️ Deleted {ticker} (No CIK)")

    print(f"✅ Done! Deleted {deleted_count} items.")

# Run the cleanup script
clean_dynamodb()

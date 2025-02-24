import boto3
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

def clean_dynamodb():
    """Scan the table and delete items where 'CIK' is missing or empty"""
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

# Example usage (if running locally)
if __name__ == "__main__":
    insert_ticker("AAPL")
    insert_ticker("TSLA")
    print("All tickers:", get_all_tickers())

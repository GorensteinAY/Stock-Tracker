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

def clean():
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

    print(f"✅ Deleted {deleted_count} items.")

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

# Example usage (if running locally)
if __name__ == "__main__":
    delete_column("Cash_Flow")

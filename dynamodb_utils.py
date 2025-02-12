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

# Example usage (if running locally)
if __name__ == "__main__":
    insert_ticker("AAPL")
    insert_ticker("TSLA")
    print("All tickers:", get_all_tickers())

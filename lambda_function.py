import json
from dynamodb_utils import insert_ticker

def lambda_handler(event, context):
    tickers = ['AAPL', 'TSLA', 'GOOGL', 'MSFT']  # Stock tickers to monitor

    for ticker in tickers:
        insert_ticker(ticker)

    return {
        'statusCode': 200,
        'body': json.dumps(f'Successfully inserted {len(tickers)} stock tickers.')
    }

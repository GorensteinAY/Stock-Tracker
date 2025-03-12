title: Stock-Tracker

Tool to identify potentially undervalued stocks

Takes a list of stocks ("Tickers.csv") 
Queries SEC to look up CIK number and generates updated CSV file ("Updated_Tickers.csv")
Uploads ticker, companny, CIK to AWS DynamoDB
Queries SEC EDGAR database for financial information (revenue, net income, net cash)
Queries Yahoo Finance for stock price and market cap
Calculates factors that could indicate whether stock is undervalued
Updates daily via AWS Lambda
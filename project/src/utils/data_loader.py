import yfinance as yf
import pandas as pd

# Sample list of Russell 1000 tickers (use full list later)
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "BRK.B", "TSLA", "UNH", "JNJ"
    # Add more tickers here, or load from a file
]

# Clean up any tickers with dash
tickers = [t.replace("-", ".") for t in tickers]

# Download
print("Downloading data...")
data = yf.download(tickers, start="2015-01-01", end="2024-12-31")['Close']

# Save
data.to_csv("r1000_close_prices.csv")
print("Saved to r1000_close_prices.csv")


import yfinance as yf
import pandas as pd

prices = pd.read_csv("data/processed/r1000_cleaned_close_prices.csv", index_col=0)
TICKERS = list(prices.columns)



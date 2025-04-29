# project/src/data_loader.py

import pandas as pd
import os

def load_close_prices(tickers, data_dir="project/data/raw/equity/"):
    prices = {}
    for ticker in tickers:
        path = os.path.join(data_dir, f"{ticker}.csv")
        df = pd.read_csv(path, usecols=["Date", "Close"], index_col="Date", parse_dates=True)
        df.rename(columns={"Close": ticker}, inplace=True)
        prices[ticker] = df

    merged = pd.concat(prices.values(), axis=1)
    return merged

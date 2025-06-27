import yfinance as yf
import pandas as pd

prices = pd.read_csv("data/processed/r1000_cleaned_close_prices.csv", index_col=0)
TICKERS = list(prices.columns)

data = []

# get fundamental info 
for ticker in TICKERS:
    try:
        info = yf.Ticker(ticker).info
        row = {
            "ticker": ticker,
            "market_cap": info.get("marketCap"),
            "book_value": info.get("bookValue"),
            "roe": info.get("returnOnEquity"),
            "total_debt": info.get("totalDebt"),
            "total_assets": info.get("totalAssets")
        }
        data.append(row)
    except Exception as e:
        print(f"Error with {ticker}: {e}")

df = pd.DataFrame(data)

# essentially same as book per share / price per share 
df["book_to_price"] = df["book_value"] / df["market_cap"]
# debt to assets
df["d2a"] = df["total_debt"] / df["total_assets"]
# market cap is there and return on equity is also there
# add date column
df["date"] = pd.Timestamp.today().normalize()
df = df[["date", "ticker", "market_cap", "book_to_price", "roe", "d2a"]]

# Save to CSV in the current directory (or change path if needed)
df.to_csv("data/processed/fundamentals_monthly.csv", index=False)
print("Saved to data/processed/fundamentals_monthly.csv")
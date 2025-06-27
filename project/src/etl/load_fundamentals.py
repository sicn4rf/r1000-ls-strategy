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

# Convert to wide format
book_to_price_df = df.pivot(index="date", columns="ticker", values="book_to_price")
roe_df = df.pivot(index="date", columns="ticker", values="roe")
d2a_df = df.pivot(index="date", columns="ticker", values="d2a")
market_cap_df = df.pivot(index="date", columns="ticker", values="market_cap")

# Save each to wide-format CSV
book_to_price_df.to_csv("data/processed/book_to_price.csv")
roe_df.to_csv("data/processed/roe.csv")
d2a_df.to_csv("data/processed/d2a.csv")
market_cap_df.to_csv("data/processed/market_cap.csv")

print("Saved fundamentals to wide-format CSVs.")
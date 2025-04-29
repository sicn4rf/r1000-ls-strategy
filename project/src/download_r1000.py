# project/src/download_r1000.py
import pandas as pd
import yfinance as yf
import os

# Step 1: Scrape Russell 1000 tickers from Wikipedia
url = "https://en.wikipedia.org/wiki/Russell_1000_Index"
tables = pd.read_html(url)

# Try to find the table with ticker symbols
russell_df = None
for table in tables:
    if any("Ticker" in str(col) or "Symbol" in str(col) for col in table.columns):
        russell_df = table
        break

if russell_df is None:
    raise ValueError("Could not find a table with a Ticker/Symbol column.")

# Try different column names for ticker symbol
for possible_col in ['Ticker', 'Symbol', 'Ticker symbol']:
    if possible_col in russell_df.columns:
        tickers = russell_df[possible_col].dropna().tolist()
        break
else:
    raise ValueError("Ticker column not found in the selected table.")

print(f"Found {len(tickers)} tickers")
print("Example tickers:", tickers[:5])

# Step 2: Prepare save directory
save_dir = "project/data/raw/equity"
os.makedirs(save_dir, exist_ok=True)

# Step 3: Download historical data for each ticker
start_date = "2023-04-19"
end_date = "2025-04-19"

for ticker in tickers:
    print(f"Downloading: {ticker}")
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if not data.empty:
            path = os.path.join(save_dir, f"{ticker}.csv")
            data.to_csv(path)
            print(f"Saved: {path}")
        else:
            print(f"No data found for {ticker}")
    except Exception as e:
        print(f"Error downloading {ticker}: {e}")

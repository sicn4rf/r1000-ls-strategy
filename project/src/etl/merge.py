import pandas as pd

# Load wide-format CSVs (tickers as columns, daily dates as rows)
quality = pd.read_csv("../../data/processed/quality_factor_daily_zscore_only.csv")
value   = pd.read_csv("../../data/processed/value_factor_z.csv")
prices  = pd.read_csv("../../data/processed/r1000_cleaned_close_prices.csv")
returns = pd.read_csv("../../data/processed/forward_returns.csv")

# Reshape to long format
quality = quality.melt(id_vars="Date", var_name="ticker", value_name="quality_z")
value   = value.melt(id_vars="Date", var_name="ticker", value_name="value_z")
prices  = prices.melt(id_vars="Date", var_name="ticker", value_name="price")
returns = returns.melt(id_vars="Date", var_name="ticker", value_name="fwd_return")

# Standardize formatting
for df_ in [quality, value, prices, returns]:
    df_["ticker"] = df_["ticker"].str.upper()
    df_["Date"] = pd.to_datetime(df_["Date"])

# Merge all on ['Date', 'ticker']
df = (
    quality
    .merge(value, on=["Date", "ticker"])
    .merge(prices, on=["Date", "ticker"])
    .merge(returns, on=["Date", "ticker"])
)

# Drop rows with missing data
df = df.dropna()


# Rename columns to match convention
df = df.rename(columns={"Date": "date", "ticker": "asset"})

# Reorder columns: [date, asset, z-scored factors, price, forward return]
df = df[["date", "asset", "quality_z", "value_z", "price", "fwd_return"]]

# Save to CSV
df.to_csv("../../data/processed/factor_matrix.csv", index=False)
print("Saved to data/processed/factor_matrix.csv") 




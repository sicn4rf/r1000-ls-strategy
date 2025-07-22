import pandas as pd

# Load wide-format CSVs (tickers as columns)
quality = pd.read_csv("../../data/processed/quality_factor_daily.csv")
value = pd.read_csv("../../data/processed/r1000_daily_pb_ratios.csv")
prices = pd.read_csv("../../data/processed/r1000_cleaned_close_prices.csv")

# Reshape to long format
quality = quality.melt(id_vars="date", var_name="ticker", value_name="quality")
value = value.melt(id_vars="date", var_name="ticker", value_name="value")
prices = prices.melt(id_vars="date", var_name="ticker", value_name="price")

# Standardize ticker format (uppercase)
quality["ticker"] = quality["ticker"].str.upper()
value["ticker"] = value["ticker"].str.upper()
prices["ticker"] = prices["ticker"].str.upper()

# Merge all datasets on ['date', 'ticker']
df = (
    quality
    .merge(value, on=["date", "ticker"])
    .merge(prices, on=["date", "ticker"])
)

# Drop rows with any missing data
df = df.dropna()

# Z-score normalize quality and value by date
df["quality_z"] = df.groupby("date")["quality"].transform(lambda x: (x - x.mean()) / x.std())
df["value_z"] = df.groupby("date")["value"].transform(lambda x: (x - x.mean()) / x.std())

# Drop original columns if desired
df = df.drop(columns=["quality", "value"])

# Save final output
df.to_csv("data/processed/factor_matrix.csv", index=False)
print("Saved to data/processed/factor_matrix.csv")



import pandas as pd

df = pd.read_csv("/Users/raunaksood/Documents/r1000-ls-strategy/project/data/raw/equity/r1000_close_prices.csv")

# remove columns where null is more than 5 percent
limit_per = len(df) * 0.05
df = df.dropna(thresh=limit_per, axis=1)
print(df.head())

df.to_csv("/Users/raunaksood/Documents/r1000-ls-strategy/project/data/processed/r1000_cleaned_close_prices.csv")
print("Saved to r1000_cleaned_close_prices.csv")
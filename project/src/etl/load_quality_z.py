import pandas as pd
from yahooquery import Ticker

# Define tickers
tickers = ['AAPL', 'AMZN', 'GOOGL', 'JNJ', 'META', 'MSFT', 'NVDA', 'TSLA', 'UNH']
t = Ticker(tickers)

# Fetch and clean
df = t.all_financial_data(frequency='a').reset_index()
quality_df = df[['symbol','asOfDate','NetIncome','StockholdersEquity','TotalDebt']].dropna()
quality_df['ROE'] = quality_df['NetIncome'] / quality_df['StockholdersEquity']
quality_df['Leverage'] = quality_df['TotalDebt'] / quality_df['StockholdersEquity']
quality_df['Quality'] = quality_df['ROE'] - quality_df['Leverage']

# Date formatting and pivot
quality_df['Date'] = pd.to_datetime(quality_df['asOfDate'])
quality_df['year'] = quality_df['Date'].dt.year
pivot = quality_df.pivot(index='year', columns='symbol', values='Quality')

# Daily index and merge
date_index = pd.date_range(
    start=f'{pivot.index.min()}-01-01',
    end=pd.Timestamp.today(),
    freq='D'
)
daily_quality = pd.DataFrame({'Date': date_index})
daily_quality['year'] = daily_quality['Date'].dt.year
daily_quality = daily_quality.merge(
    pivot,
    how='left',
    left_on='year',
    right_index=True
).drop(columns='year')

# Compute z-scores
for ticker in tickers:
    if ticker in daily_quality.columns:
        daily_quality[f"{ticker}_z"] = (
            daily_quality[ticker] - daily_quality[ticker].mean()
        ) / daily_quality[ticker].std()

# Save full CSV with z-scores
daily_quality.to_csv("../../data/processed/quality_factor_daily_full.csv", index=False)

# Filter rows where all z-scores are present
zscore_cols = [f"{ticker}_z" for ticker in tickers if f"{ticker}_z" in daily_quality.columns]
filtered = daily_quality[['Date'] + zscore_cols].dropna()

# Save filtered z-score CSV
filtered.to_csv("../../data/processed/quality_factor_daily_zscore_only.csv", index=False)

print("Saved both CSVs:")
print("   - quality_factor_daily_full.csv (full data with z-scores)")
print("   - quality_factor_daily_zscore_only.csv (filtered rows where all z-scores are present)")


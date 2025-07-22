import pandas as pd
from yahooquery import Ticker

# Define the tickers you want to analyze
tickers = ['aapl', 'amzn', 'googl', 'jnj', 'meta', 'msft', 'nvda', 'tsla', 'unh']

# Initialize the yahooquery Ticker object
t = Ticker(tickers)

# Fetch all available financial data (annual reports only)
df = t.all_financial_data(frequency='a')  # annual data
df = df.reset_index()

# Select relevant columns and drop rows with missing values
quality_df = df[['symbol', 'asOfDate', 'NetIncome', 'StockholdersEquity', 'TotalDebt']].dropna()

# Compute ROE and Leverage
quality_df['ROE'] = quality_df['NetIncome'] / quality_df['StockholdersEquity']
quality_df['Leverage'] = quality_df['TotalDebt'] / quality_df['StockholdersEquity']
quality_df['Quality'] = quality_df['ROE'] - quality_df['Leverage']

# Convert asOfDate to datetime and extract year
quality_df['asOfDate'] = pd.to_datetime(quality_df['asOfDate'])
quality_df['year'] = quality_df['asOfDate'].dt.year

# Pivot to have (year x ticker) table for Quality
pivot = quality_df.pivot(index='year', columns='symbol', values='Quality')

# Build complete year range from 10 years ago to now
start_year = pd.Timestamp.today().year - 10
end_year = pd.Timestamp.today().year
all_years = range(start_year, end_year + 1)

# Reindex and fill missing values
pivot = pivot.reindex(all_years)
pivot = pivot.bfill().ffill()  # Backfill earliest years, forward-fill latest

# Create daily date range for the last 10 years
date_index = pd.date_range(start=f'{start_year}-01-01', end=pd.Timestamp.today(), freq='D')

# Create daily DataFrame and map each date to its corresponding year's Quality values
daily_quality = pd.DataFrame(index=date_index)
daily_quality['year'] = daily_quality.index.year
daily_quality = daily_quality.merge(pivot, how='left', left_on='year', right_index=True)
daily_quality = daily_quality.drop(columns='year')
df = pd.DataFrame(daily_quality)
# Save result
df.to_csv('../../data/processed/quality_factor_daily.csv')
print("Saved quality_factor_daily.csv with daily values over 10 years.")










import pandas as pd
from yahooquery import Ticker

# Define tickers
tickers = ['AAPL', 'AMZN', 'GOOGL', 'JNJ', 'META', 'MSFT', 'NVDA', 'TSLA', 'UNH']
t = Ticker(tickers)

# Fetch fundamentals and reset index
df = t.all_financial_data(frequency='a').reset_index()

# Select and clean
quality_df = df[['symbol','asOfDate','NetIncome','StockholdersEquity','TotalDebt']].dropna()
quality_df['ROE']      = quality_df['NetIncome'] / quality_df['StockholdersEquity']
quality_df['Leverage'] = quality_df['TotalDebt']  / quality_df['StockholdersEquity']
quality_df['Quality']  = quality_df['ROE'] - quality_df['Leverage']

# Convert to datetime and extract year
quality_df['Date'] = pd.to_datetime(quality_df['asOfDate'])
quality_df['year'] = quality_df['Date'].dt.year

# Pivot to (year × ticker) using only the years present
pivot = quality_df.pivot(index='year', columns='symbol', values='Quality')

# Build daily index over the full span you care about
date_index = pd.date_range(
    start=f'{pivot.index.min()}-01-01',
    end=pd.Timestamp.today(),
    freq='D'
)

# Map each date to its year's quality values (NaN if that year wasn’t in your data)
daily_quality = pd.DataFrame({'Date': date_index})
daily_quality['year'] = daily_quality['Date'].dt.year
daily_quality = daily_quality.merge(
    pivot,
    how='left',
    left_on='year',
    right_index=True
).drop(columns='year')

# Save—with Date as a real column and no extra index
daily_quality.to_csv(
    '../../data/processed/quality_factor_daily.csv',
    index=False
)
print("Saved quality_factor_daily.csv with daily values (no fill) over actual years present.")











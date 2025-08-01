import pandas as pd
import yahooquery as yq
import numpy as np
from pathlib import Path

def load_price_data():

    # Load the cleaned price data from CSV file.
    
    # Returns:
    #     pd.DataFrame: DataFrame containing daily closing prices for all stocks
    #                  Expected format: dates as index, stock tickers as columns

    price_file_path = Path(__file__).parents[2] / "data" / "processed" / "r1000_cleaned_close_prices.csv"
    
    # Read the CSV file - the Date column should be used as index
    # The file has structure: unnamed_index, Date, AAPL, AMZN, GOOGL, etc.
    price_df = pd.read_csv(price_file_path)
    
    # Set Date column as index and drop the unnamed first column
    price_df = price_df.set_index('Date')
    price_df.index = pd.to_datetime(price_df.index)
    
    # Drop the unnamed first column (which contains 0,1,2,3...)
    if len(price_df.columns) > 0:
        first_col_name = str(price_df.columns[0])
        if first_col_name.startswith('Unnamed'):
            price_df = price_df.drop(columns=[first_col_name])
    
    print(f"Loaded price data: {price_df.shape[0]} dates, {price_df.shape[1]} stocks")
    print(f"Date range: {price_df.index.min()} to {price_df.index.max()}")
    print(f"Stock tickers: {list(price_df.columns)}")
    
    return price_df

def get_detailed_book_value_data(ticker_symbol):

    # Extract detailed tangible book value data for verification purposes.
    
    # Returns all available annual data including:
    # - Fiscal year end date
    # - Tangible Book Value (total)
    # - Ordinary Shares Number (shares outstanding)
    # - Book Value Per Share (calculated)
    
    # Args:
    #     ticker_symbol (str): Stock ticker symbol (e.g., 'AAPL')
    
    # Returns:
    #     pd.DataFrame: DataFrame with detailed financial data by year
    #                  Returns None if no data available

    try:
        # Create yahooquery Ticker object for the stock
        ticker = yq.Ticker(ticker_symbol)
        
        # Get balance sheet data (returns annual financial statements)
        balance_sheet = ticker.balance_sheet()
        
        # Filter for rows that have both book value and shares data
        valid_data = balance_sheet[
            balance_sheet['StockholdersEquity'].notna() & 
            balance_sheet['OrdinarySharesNumber'].notna()
        ].copy()
        
        if len(valid_data) == 0:
            print(f"  No valid book value data for {ticker_symbol}")
            return None
        
        # Create detailed breakdown DataFrame
        detailed_data = pd.DataFrame({
            'Ticker': ticker_symbol,
            'Fiscal_Year_End': pd.to_datetime(valid_data['asOfDate']),
            'Total_Book_Value': valid_data['StockholdersEquity'],
            'Shares_Outstanding': valid_data['OrdinarySharesNumber'],
            'Book_Value_Per_Share': valid_data['StockholdersEquity'] / valid_data['OrdinarySharesNumber']
        })
        
        # Sort by fiscal year end date
        detailed_data = detailed_data.sort_values('Fiscal_Year_End')
        
        print(f"  {ticker_symbol}: Found {len(detailed_data)} years of detailed data")
        return detailed_data
        
    except Exception as e:
        print(f"  Error getting detailed book value data for {ticker_symbol}: {e}")
        return None

def create_book_value_verification_csv(tickers):

    # Create a comprehensive CSV file showing detailed book value calculations
    # for verification purposes.
    
    # Args:
    #     tickers (list): List of stock ticker symbols

    print("\nCreating detailed book value verification CSV...")
    
    all_detailed_data = []
    
    # Loop through each stock ticker
    for i, ticker in enumerate(tickers):
        print(f"Processing {i+1}/{len(tickers)}: {ticker}")
        
        # Get detailed book value data for this stock
        detailed_data = get_detailed_book_value_data(ticker)
        
        if detailed_data is not None:
            all_detailed_data.append(detailed_data)
    
    if all_detailed_data:
        # Combine all data into one DataFrame
        verification_df = pd.concat(all_detailed_data, ignore_index=True)
        
        # Format the data for better readability
        verification_df['Fiscal_Year_End'] = verification_df['Fiscal_Year_End'].dt.strftime('%Y-%m-%d')
        verification_df['Total_Book_Value'] = verification_df['Total_Book_Value'].round(0)
        verification_df['Shares_Outstanding'] = verification_df['Shares_Outstanding'].round(0)
        verification_df['Book_Value_Per_Share'] = verification_df['Book_Value_Per_Share'].round(4)
        
        # Save to CSV
        output_path = "../../data/processed/book_value_verification.csv"
        verification_df.to_csv(output_path, index=False)
        
        print(f"\nVerification data saved to: {output_path}")
        print(f"Total records: {len(verification_df)} across {len(tickers)} stocks")
        
def get_historical_book_values(ticker_symbol):

    # Extract ALL historical book value per share data for a given stock.
    
    # Uses yahooquery to get:
    # - balance_sheet(): Gets historical balance sheet data (annual)
    # - StockholdersEquity: Total book value (includes all assets)
    # - OrdinarySharesNumber: Total shares outstanding
    
    # Args:
    #     ticker_symbol (str): Stock ticker symbol (e.g., 'AAPL')
    
    # Returns:
    #     pd.Series: Series with fiscal year-end dates as index and book value per share as values
    #               Returns None if no data available

    try:
        # Create yahooquery Ticker object for the stock
        ticker = yq.Ticker(ticker_symbol)
        
        # Get balance sheet data (returns annual financial statements)
        balance_sheet = ticker.balance_sheet()
        
        # Filter for rows that have both book value and shares data
        valid_data = balance_sheet[
            balance_sheet['StockholdersEquity'].notna() & 
            balance_sheet['OrdinarySharesNumber'].notna()
        ].copy()
        
        if len(valid_data) == 0:
            print(f"  No valid book value data for {ticker_symbol}")
            return None
        
        # Calculate book value per share for each year
        valid_data['BookValuePerShare'] = (
            valid_data['StockholdersEquity'] / valid_data['OrdinarySharesNumber']
        )
        
        # Create a Series with fiscal year-end dates as index
        book_value_series = pd.Series(
            valid_data['BookValuePerShare'].values,
            index=pd.to_datetime(valid_data['asOfDate'])
        ).sort_index()
        
        print(f"  {ticker_symbol}: Found {len(book_value_series)} years of book value data")
        return book_value_series
        
    except Exception as e:
        print(f"  Error getting book value for {ticker_symbol}: {e}")
        return None

def get_rolling_book_value_per_share(price_dates, book_value_series):

    # Create a rolling book value per share series that updates annually.
    
    # For each date, use the most recent annual book value available at that time.
    # Example: For Jan 1, 2025, use 2024's book value per share.
    
    # Args:
    #     price_dates (pd.DatetimeIndex): All dates from the price data
    #     book_value_series (pd.Series): Historical book values with fiscal year-end dates
    
    # Returns:
    #     pd.Series: Rolling book value per share for each price date

    if book_value_series is None or len(book_value_series) == 0:
        return pd.Series(np.nan, index=price_dates)
    
    
    # For each price date, find the most recent book value available
    rolling_book_values = []
    
    for date in price_dates:
        # Convert date to pandas Timestamp for comparison
        date = pd.Timestamp(date)
        
        # Find book values that are available before or on this date
        available_book_values = book_value_series[book_value_series.index <= date]
        
        if len(available_book_values) > 0:
            # Use the most recent book value available
            most_recent_book_value = available_book_values.iloc[-1]
            rolling_book_values.append(most_recent_book_value)
        else:
            # No book value data available for this date yet
            rolling_book_values.append(np.nan)
    
    return pd.Series(rolling_book_values, index=price_dates)

def calculate_daily_pb_ratios(price_df):

    # Calculate daily Price-to-Book (PB) ratios for all stocks using rolling book values.
    
    # Formula: PB Ratio = Daily Share Price / Rolling Book Value Per Share
    # Where Rolling Book Value Per Share uses the most recent annual data available at each date.
    
    # Args:
    #     price_df (pd.DataFrame): DataFrame with daily prices (dates as index, tickers as columns)
    
    # Returns:
    #     pd.DataFrame: DataFrame with daily PB ratios (same structure as input)

    # Create empty DataFrame to store PB ratios (same structure as price data)
    pb_ratios_df = price_df.copy()
    
    # Get list of all stock tickers from the price data columns
    tickers = price_df.columns.tolist()
    print(f"\nCalculating rolling PB ratios for {len(tickers)} stocks...")
    
    # Loop through each stock ticker
    for i, ticker in enumerate(tickers):
        print(f"Processing {i+1}/{len(tickers)}: {ticker}")
        
        # Get ALL historical book values for this stock
        historical_book_values = get_historical_book_values(ticker)
        
        if historical_book_values is None:
            # If no book value data, set all PB ratios to NaN
            pb_ratios_df[ticker] = np.nan
            continue
        
        # Create rolling book value series that updates annually
        rolling_book_values = get_rolling_book_value_per_share(
            price_df.index, historical_book_values
        )
        
        # Calculate daily PB ratios: Daily Price / Rolling Book Value Per Share
        daily_prices = price_df[ticker]
        daily_pb_ratios = daily_prices / rolling_book_values
        
        # Store the calculated PB ratios
        pb_ratios_df[ticker] = daily_pb_ratios

        pb_ratios_df[ticker] = (pb_ratios_df[ticker] - pb_ratios_df[ticker].mean()) / pb_ratios_df[ticker].std()
        
        print(f"    Applied {len(historical_book_values)} different book values across time period")
    
    return pb_ratios_df

def save_pb_ratios_to_csv(pb_ratios_df):

    # Save the calculated daily PB ratios to a CSV file, preserving the Date column.
    
    # Args:
    #     pb_ratios_df (pd.DataFrame): DataFrame containing daily PB ratios

    # Define output file path
    output_path = "../../data/processed/value_factor.csv"
    
    # Save to CSV with date index preserved as "Date" column
    # The index_label parameter ensures the date column is named "Date"
    pb_ratios_df.to_csv(output_path, index_label="Date")
    
    print(f"\nPB ratios saved to: {output_path}")
    print(f"Data shape: {pb_ratios_df.shape[0]} dates, {pb_ratios_df.shape[1]} stocks")
    print("Date column preserved in output CSV")

def filter_complete_rows(input_csv, output_csv):
    """
    Keep only rows where all columns except 'Date' are present (no missing values).
    """
    import pandas as pd
    df = pd.read_csv(input_csv)
    # Drop rows with any missing values except in 'Date'
    cols_to_check = [col for col in df.columns if col != 'Date']
    df_clean = df.dropna(subset=cols_to_check)
    df_clean.to_csv(output_csv, index=False)
    print(f"Filtered CSV saved to {output_csv} ({len(df_clean)} rows)")

def filter_zscore_complete_rows(input_csv, output_csv):
    """
    Save only rows with all z-score columns (ending with '_z') and Date present (no missing values).
    """
    import pandas as pd
    df = pd.read_csv(input_csv)
    # Select only Date and columns ending with '_z'
    z_cols = [col for col in df.columns if col != 'Date']
    df_z_clean = df.dropna(subset=z_cols)

    df_z_clean.to_csv(output_csv, index=False)
    print(f"Filtered z-score CSV saved to {output_csv} ({len(df_z_clean)} rows)")

def main():

    # Main function that orchestrates the entire rolling PB ratio calculation process.
    
    # Steps:
    # 1. Load daily price data from CSV
    # 2. Create detailed book value verification CSV
    # 3. Get ALL historical book values for each stock using yahooquery
    # 4. Calculate daily PB ratios using rolling/time-varying book values that update annually
    # 5. Save results to CSV file with Date column preserved
    
    # Rolling Logic:
    # - For each date, use the most recent annual book value available at that time
    # - Example: Jan 1, 2025 uses 2024's book value; Jan 1, 2024 uses 2023's book value

    print("=== Rolling Daily PB Ratio Calculation with Verification ===\n")
    
    # Step 1: Load the daily price data
    print("Step 1: Loading price data...")
    price_df = load_price_data()
    
    # Get list of tickers for verification
    tickers = price_df.columns.tolist()
    
    # Step 2: Create detailed verification CSV
    print("\nStep 2: Creating detailed book value verification data...")
    create_book_value_verification_csv(tickers)
    
    # Step 3 & 4: Calculate rolling daily PB ratios for all stocks
    print("\nStep 3: Calculating rolling daily PB ratios...")
    pb_ratios_df = calculate_daily_pb_ratios(price_df)
    
    # Step 5: Save results to CSV with Date column preserved
    print("\nStep 4: Saving results...")
    save_pb_ratios_to_csv(pb_ratios_df)
    # Filter for complete rows only (no missing values except Date)
    filter_complete_rows(
        "../../data/processed/value_factor.csv",
        "../../data/processed/value_factor.csv"
    )
    # Save only complete z-score rows to value_factor_z.csv
    filter_zscore_complete_rows(
        "../../data/processed/value_factor.csv",
        "../../data/processed/value_factor_z.csv"
    )

    pb_ratios_df[['AAPL']].to_csv("../../data/processed/test_z.csv")
    
    print("\n=== Process Complete ===")
    print("Files created:")
    print("1. book_value_verification.csv - Detailed breakdown of book value calculations")
    print("2. value_factor.csv - Daily PB ratios using rolling book values")
    print("3. value_factor_z.csv - Only rows with all z-score columns present")

# Run the main function when script is executed
if __name__ == "__main__":
    main()
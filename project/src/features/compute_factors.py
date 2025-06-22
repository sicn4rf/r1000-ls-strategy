
# Factor computation layer.

# Each function returns a **DataFrame** aligned to the input index/columns.
# All factors are expressed so that a **higher value == stronger long signal**.


import pandas as pd
import numpy as np

# --------------------------------------------------------------------- #
# Momentum (12-1)
# --------------------------------------------------------------------- #
def momentum(prices: pd.DataFrame,
             lookback: int = 252,
             skip: int = 21) -> pd.DataFrame:
    # 12-month total return minus most recent 1-month return.

    # subtract one month to prevent recent spikes from affecting mean

    prices = prices.sort_index()

    # Log returns: r_t = log(P_t / P_{t-d})
    long_return = np.log(prices / prices.shift(lookback))
    short_return = np.log(prices / prices.shift(skip))

    momentum_signal = long_return - short_return

    # Lag 1 day to avoid lookahead bias
    return momentum_signal.shift(1)


# --------------------------------------------------------------------- #
# Value (book-to-price)
# --------------------------------------------------------------------- #
def value(book_to_price: pd.DataFrame) -> pd.DataFrame:
    
    # Already pre-computed fundamental ratio; identity passthrough.

    return book_to_price


# --------------------------------------------------------------------- #
# Size (market-cap)
# --------------------------------------------------------------------- #
def size(mkt_cap: pd.DataFrame) -> pd.DataFrame:

    # Inverse so that SMALLER firms → larger positive signal.

    # smaller firms have shown to have better returns for reasons
    # like they have higher chance to grow faster. long the small firm
    # short the mega firms
    
    return -np.log(mkt_cap)


# --------------------------------------------------------------------- #
# Quality (ROE – leverage)
# --------------------------------------------------------------------- #
def quality(roe: pd.DataFrame,
            d2a: pd.DataFrame) -> pd.DataFrame:
    
    #Composite: high ROE, low leverage.

    # long stocks with a high ROE but low debt to assets

    # quality factor finds comapanies that are profit efficient and 
    # low debt while punishing low roe and high debt 

    return roe.rank(axis=1, pct=True) - d2a.rank(axis=1, pct=True)


# --------------------------------------------------------------------- #
# Volatility (1-Y σ)
# --------------------------------------------------------------------- #
def low_vol(prices: pd.DataFrame,
            window: int = 252) -> pd.DataFrame:
    
    # Lower σ => stronger signal. so a big stddev of %change will mean 
    # more "wobbly", so make it negative so it pushes this type of stock
    # to the bottom of the list, go short.
    prices = prices.sort_index()
    log_returns = np.log(prices / prices.shift(1))
    rolling_vol = log_returns.rolling(window=window, min_periods=window).std()
    return -rolling_vol.shift(1)  # lag to prevent leakage


# --------------------------------------------------------------------- #
# Sentiment (placeholder for NLP scores)
# --------------------------------------------------------------------- #
def sentiment(nlp_scores: pd.DataFrame) -> pd.DataFrame:
    
    # Higher positive language => stronger long signal.
    
    return nlp_scores
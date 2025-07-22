
# Compute N-day forward log-returns and write to parquet.

# Example:
# python -m compute_forward_returns \
#     --prices data/processed/prices_cleaned.csv \
#     --horizon 63 \
#     --out data/processed/forward_returns.csv

from pathlib import Path
import argparse
import pandas as pd
import numpy as np

def forward_log_returns(df: pd.DataFrame, horizon: int) -> pd.DataFrame:

    # df: wide price table (index=Date, columns=tickers, level=AdjClose)
    # horizon: trading-day look-ahead (≈63 ≈ 3 months)

    return np.log(df).diff(horizon).shift(-horizon)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prices", required=True)
    ap.add_argument("--horizon", type=int, default=63)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    prices = pd.read_csv(args.prices, index_col=0).set_index("Date")
    fwd = forward_log_returns(prices, args.horizon)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    fwd.reset_index().to_csv(args.out, index=False)
    print(f"forward returns -> {args.out}")

if __name__ == "__main__":
    main()
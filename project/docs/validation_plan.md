# Data-Validation Rules (v0)

| Check | Rule | Why? |
|-------|------|------|
| Missing values per ticker | drop if **> 5 %** NaNs | sparse price paths break factor calc |
| Small gaps | `ffill` then `bfill` (≤ 3 trading days) | keeps continuity w/o major look-ahead bias |
| Residual NaNs | drop row | guarantee model-ready matrices |

*(add notes as rules evolve)*
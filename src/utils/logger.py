from pathlib import Path
from datetime import datetime
import pandas as pd

LOG_FILE = Path("logs/data_validation_log.txt")

def append_validation_entry(raw: pd.DataFrame, clean: pd.DataFrame,
                            dropped: list[str]) -> None:
    
    # Append a single-line audit entry after every validation run.
    LOG_FILE.parent.mkdir(exist_ok=True, parents=True)
    line = (
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] "
        f"raw={raw.shape} clean={clean.shape} "
        f"dropped={dropped} nulls={clean.isna().sum().sum()}"
    )
    with LOG_FILE.open("a") as f:
        f.write(line + "\n")
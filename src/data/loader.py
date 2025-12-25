"""
Data loader for historical OHLCV market data.
"""
import pandas as pd
from typing import Optional, Dict


class DataLoader:
    def __init__(self, filepath: str):
        """
        Initialize the loader with a path to a CSV file.
        """
        self.filepath = filepath
        self.data: Optional[pd.DataFrame] = None

    def load_csv(self) -> pd.DataFrame:
        """
        Load OHLCV data from CSV file into a pandas DataFrame.

        Expected columns (yfinance-style): Date index or 'Date' column,
        and OHLCV columns: Open, High, Low, Close, Volume, Adj Close.
        """
        # Read CSV normally
        df = pd.read_csv(self.filepath)

        # If yfinance saved with index, first column likely is 'Date'
        # or an unnamed index column.
        # Handle common patterns:
        # 1) 'Date' column present
        # 2) first column is unnamed but contains dates
        # 3) extra non-price columns like 'Ticker' present
        date_col = None
        if "Date" in df.columns:
            date_col = "Date"
        elif "Datetime" in df.columns:
            date_col = "Datetime"
        else:
            # Try using the first column as date-like
            first_col = df.columns[0]
            date_col = first_col

        # Parse dates safely
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        # Drop rows where date could not be parsed (like header junk)
        df = df.dropna(subset=[date_col])
        df = df.set_index(date_col)

        # Keep only standard OHLCV if present
        keep_cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
        df = df[keep_cols]

        # Sort by time just in case
        self.data = df.sort_index()
        return self.data

    def get_current_state(self, index: int) -> Dict:
        """
        Get market state (one time step) as a simple dict.

        Example output:
        {
            "price": 150.5,
            "open": ...,
            "high": ...,
            "low": ...,
            "close": ...,
            "volume": ...,
            "index": index
        }
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_csv() first.")

        if index < 0 or index >= len(self.data):
            raise IndexError(f"Index {index} out of range [0, {len(self.data)-1}]")

        row = self.data.iloc[index]
        state = {
            "open": float(row.get("Open", 0.0)),
            "high": float(row.get("High", 0.0)),
            "low": float(row.get("Low", 0.0)),
            "close": float(row.get("Close", 0.0)),
            "volume": float(row.get("Volume", 0.0)),
            "price": float(row.get("Close", 0.0)),  # alias for convenience
            "index": index,
        }
        return state

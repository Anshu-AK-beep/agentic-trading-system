"""
Data loader for historical OHLCV market data.
"""
import pandas as pd
from typing import Optional

class DataLoader:
    def __init__(self):
        pass
    
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """Load OHLCV data from CSV file."""
        raise NotImplementedError
    
    def get_current_state(self, index: int) -> dict:
        """Get market state at specific time step."""
        raise NotImplementedError

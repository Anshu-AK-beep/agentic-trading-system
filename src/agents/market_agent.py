"""
Market Analysis Agent: Analyzes OHLCV → Buy/Sell/Hold signals.

Initial strategy: Simple Moving Average (SMA) crossover.
- If price > SMA(window_short) and SMA(window_short) > SMA(window_long): BUY
- If price < SMA(window_short) and SMA(window_short) < SMA(window_long): SELL
- Else: HOLD
"""
from typing import Dict
import pandas as pd


class MarketAnalysisAgent:
    def __init__(self, data: pd.DataFrame, short_window: int = 5, long_window: int = 20):
        """
        data: full OHLCV DataFrame (indexed by datetime).
        short_window: short SMA length.
        long_window: long SMA length.
        """
        self.data = data
        self.short_window = short_window
        self.long_window = long_window

        # Precompute indicators
        self.data["sma_short"] = self.data["Close"].rolling(window=self.short_window).mean()
        self.data["sma_long"] = self.data["Close"].rolling(window=self.long_window).mean()

    def analyze(self, market_state: Dict) -> Dict:
        """
        Returns a trading signal based on SMA crossover.

        Output example:
        {
            "action": "buy" / "sell" / "hold",
            "confidence": float,  # 0.0 - 1.0
            "target_price": float
        }
        """
        idx = market_state["index"]
        # Need enough history to compute both SMAs
        if idx < self.long_window:
            return {"action": "hold", "confidence": 0.0, "target_price": market_state["price"]}

        row = self.data.iloc[idx]
        sma_short = row["sma_short"]
        sma_long = row["sma_long"]
        price = market_state["price"]

        if pd.isna(sma_short) or pd.isna(sma_long):
            return {"action": "hold", "confidence": 0.0, "target_price": price}

        # Simple crossover logic
        # Replace the crossover logic with this simpler version:
        if price > sma_short:
            return {"action": "buy", "confidence": 0.6, "target_price": price}
        elif price < sma_short:
            return {"action": "sell", "confidence": 0.6, "target_price": price}
        else:
            return {"action": "hold", "confidence": 0.1, "target_price": price}


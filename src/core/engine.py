"""
Main simulation engine that runs time steps.
"""
from typing import Dict

class TradingEngine:
    def __init__(self):
        self.order_book = None
        self.portfolio = {'cash': 100000, 'position': 0}
        self.trades: list = []
        self.current_step = 0
    
    def step(self, market_state: Dict) -> Dict:
        """Execute one time step."""
        raise NotImplementedError
    
    def get_portfolio_value(self, current_price: float) -> float:
        raise NotImplementedError

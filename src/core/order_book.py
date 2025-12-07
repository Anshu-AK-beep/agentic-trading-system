"""
Limit Order Book implementation with matching logic.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Order:
    order_id: str
    side: str      # 'buy' or 'sell'
    price: float
    quantity: float
    timestamp: int

class OrderBook:
    def __init__(self):
        self.bids: Dict[float, float] = {}  # price -> quantity
        self.asks: Dict[float, float] = {}
        self.next_order_id = 0
    
    def place_order(self, order: Order) -> List[Order]:
        """Place order and return matched trades."""
        raise NotImplementedError
    
    def get_best_bid(self) -> Optional[float]:
        raise NotImplementedError
    
    def get_best_ask(self) -> Optional[float]:
        raise NotImplementedError

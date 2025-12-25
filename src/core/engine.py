"""
Main simulation engine that runs time steps.
"""
from typing import Dict, List
from src.core.order_book import OrderBook, Trade


class TradingEngine:
    def __init__(self, starting_cash: float = 100_000.0):
        self.order_book = OrderBook()
        self.cash: float = starting_cash
        self.position: float = 0.0
        self.trades: List[Trade] = []
        self.current_step: int = 0

    def place_and_execute_orders(self, orders: List[Dict], timestamp: int):
        """
        Place each order in the order book and update cash/position based on trades.
        """
        for order in orders:
            side = order["side"]
            price = order["price"]
            qty = order["quantity"]

            # ADD FAKE COUNTERPARTY LIQUIDITY for simulation
            if side == "buy":
                # Add fake sell orders at current price
                self.order_book.place_order("sell", price, qty * 2, timestamp)
            else:
                # Add fake buy orders at current price  
                self.order_book.place_order("buy", price, qty * 2, timestamp)

            trades = self.order_book.place_order(side=side, price=price, quantity=qty, timestamp=timestamp)
            for t in trades:
                self.trades.append(t)
                if side == "buy":
                    self.position += t.quantity
                    self.cash -= t.quantity * t.price
                else:
                    self.position -= t.quantity
                    self.cash += t.quantity * t.price

    def step(self, market_state: Dict) -> Dict:
        self.current_step = market_state.get("index", self.current_step)
        price = market_state["price"]
        portfolio_value = self.get_portfolio_value(price)

        return {
            "step": self.current_step,
            "price": price,
            "cash": self.cash,
            "position": self.position,
            "portfolio_value": portfolio_value,
        }

    def get_portfolio_value(self, current_price: float) -> float:
        return self.cash + self.position * current_price

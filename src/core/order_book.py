"""
Optimized Limit Order Book implementation with efficient matching logic.
Uses SortedDict for O(log n) operations instead of O(n).
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from sortedcontainers import SortedDict


@dataclass
class Order:
    order_id: int
    side: str        # 'buy' or 'sell'
    price: float
    quantity: float
    timestamp: int


@dataclass
class Trade:
    buy_order_id: int
    sell_order_id: int
    price: float
    quantity: float
    timestamp: int


class OrderBook:
    """
    Optimized order book using SortedDict for O(log n) operations:
    - Fast best bid/ask retrieval
    - Efficient order insertion and matching
    - Aggregated by price level
    """

    def __init__(self):
        # Use SortedDict for O(log n) operations
        self.bids: SortedDict = SortedDict()  # price -> quantity (descending)
        self.asks: SortedDict = SortedDict()  # price -> quantity (ascending)
        self.next_order_id: int = 1
        
        # Statistics for monitoring
        self.total_volume: float = 0.0
        self.trade_count: int = 0

    def _get_best_bid_price(self) -> Optional[float]:
        """O(1) operation with SortedDict"""
        return self.bids.keys()[-1] if self.bids else None

    def _get_best_ask_price(self) -> Optional[float]:
        """O(1) operation with SortedDict"""
        return self.asks.keys()[0] if self.asks else None

    def get_best_bid(self) -> Optional[float]:
        return self._get_best_bid_price()

    def get_best_ask(self) -> Optional[float]:
        return self._get_best_ask_price()
    
    def get_spread(self) -> Optional[float]:
        """Calculate bid-ask spread"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid and best_ask:
            return best_ask - best_bid
        return None
    
    def get_mid_price(self) -> Optional[float]:
        """Calculate mid-market price"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid and best_ask:
            return (best_bid + best_ask) / 2.0
        return None
    
    def get_depth(self, levels: int = 5) -> Dict:
        """Get order book depth for visualization"""
        bid_levels = []
        ask_levels = []
        
        # Get top N bid levels
        for i, (price, qty) in enumerate(reversed(self.bids.items())):
            if i >= levels:
                break
            bid_levels.append({"price": price, "quantity": qty})
        
        # Get top N ask levels
        for i, (price, qty) in enumerate(self.asks.items()):
            if i >= levels:
                break
            ask_levels.append({"price": price, "quantity": qty})
        
        return {
            "bids": bid_levels,
            "asks": ask_levels,
            "spread": self.get_spread(),
            "mid_price": self.get_mid_price()
        }

    def place_order(self, side: str, price: float, quantity: float, timestamp: int) -> List[Trade]:
        """
        Place a new limit order and try to match it against the book.
        Returns a list of trades that got executed.
        
        Optimized with SortedDict for faster matching.
        """
        order_id = self.next_order_id
        self.next_order_id += 1
        order = Order(order_id=order_id, side=side, price=price, quantity=quantity, timestamp=timestamp)

        trades: List[Trade] = []

        if side == "buy":
            trades = self._match_buy(order)
        elif side == "sell":
            trades = self._match_sell(order)
        else:
            raise ValueError("side must be 'buy' or 'sell'")
        
        # Update statistics
        for trade in trades:
            self.total_volume += trade.quantity * trade.price
            self.trade_count += 1

        return trades

    def _match_buy(self, order: Order) -> List[Trade]:
        """Optimized buy order matching"""
        trades: List[Trade] = []

        # While we have quantity left and there is at least one ask <= buy price
        while order.quantity > 0:
            best_ask = self._get_best_ask_price()
            if best_ask is None or best_ask > order.price:
                break  # no more matching possible

            available_qty = self.asks[best_ask]
            trade_qty = min(order.quantity, available_qty)

            trades.append(
                Trade(
                    buy_order_id=order.order_id,
                    sell_order_id=-1,
                    price=best_ask,
                    quantity=trade_qty,
                    timestamp=order.timestamp,
                )
            )

            # Update quantities
            order.quantity -= trade_qty
            self.asks[best_ask] -= trade_qty
            if self.asks[best_ask] <= 0:
                del self.asks[best_ask]

        # If remaining quantity > 0, add to bids
        if order.quantity > 0:
            if order.price in self.bids:
                self.bids[order.price] += order.quantity
            else:
                self.bids[order.price] = order.quantity

        return trades

    def _match_sell(self, order: Order) -> List[Trade]:
        """Optimized sell order matching"""
        trades: List[Trade] = []

        while order.quantity > 0:
            best_bid = self._get_best_bid_price()
            if best_bid is None or best_bid < order.price:
                break

            available_qty = self.bids[best_bid]
            trade_qty = min(order.quantity, available_qty)

            trades.append(
                Trade(
                    buy_order_id=-1,
                    sell_order_id=order.order_id,
                    price=best_bid,
                    quantity=trade_qty,
                    timestamp=order.timestamp,
                )
            )

            order.quantity -= trade_qty
            self.bids[best_bid] -= trade_qty
            if self.bids[best_bid] <= 0:
                del self.bids[best_bid]

        # If remaining quantity > 0, add to asks
        if order.quantity > 0:
            if order.price in self.asks:
                self.asks[order.price] += order.quantity
            else:
                self.asks[order.price] = order.quantity

        return trades
    
    def clear(self):
        """Clear the order book"""
        self.bids.clear()
        self.asks.clear()
        self.total_volume = 0.0
        self.trade_count = 0
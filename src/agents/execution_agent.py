"""
Execution Agent: Turns approved trade decisions into concrete orders.
"""
from typing import Dict, List


class ExecutionAgent:
    def __init__(self):
        pass

    def build_orders(self, decision: Dict, market_state: Dict) -> List[Dict]:
        """
        decision: output from RiskManagementAgent
        market_state: current market info

        Returns list of order dicts:
        [
          {"side": "buy" / "sell", "price": float, "quantity": float}
        ]
        """
        if not decision.get("approved", False):
            return []

        max_size = decision.get("max_size", 0.0)
        if max_size <= 0:
            return []

        # For now: simple limit order at current price
        price = market_state["price"]

        action = decision.get("action", "hold")
        if action not in ("buy", "sell"):
            # RiskAgent currently doesn't copy action; we’ll set it there in a moment
            return []

        return [{
            "side": action,
            "price": float(price),
            "quantity": float(max_size),
        }]

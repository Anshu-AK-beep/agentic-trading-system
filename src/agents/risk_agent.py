"""
Risk Management Agent: Position sizing, stop-loss, exposure limits.
"""
from typing import Dict


class RiskManagementAgent:
    def __init__(self, max_position: float = 1000, max_single_trade: float = 100):
        self.max_position = max_position
        self.max_single_trade = max_single_trade

    def approve_trade(self, proposal: Dict, portfolio: Dict) -> Dict:
        action = proposal.get("action", "hold")
        if action == "hold":
            return {"approved": False, "max_size": 0.0, "reason": "No trade (hold)", "action": action}

        current_position = portfolio.get("position", 0.0)

        if action == "buy":
            remaining = self.max_position - current_position
            max_size = min(self.max_single_trade, max(0.0, remaining))
        elif action == "sell":
            max_size = min(self.max_single_trade, max(0.0, current_position))
        else:
            return {"approved": False, "max_size": 0.0, "reason": "Unknown action", "action": action}

        if max_size <= 0:
            return {"approved": False, "max_size": 0.0, "reason": "Risk limit reached", "action": action}

        return {"approved": True, "max_size": max_size, "reason": "Within risk limits", "action": action}

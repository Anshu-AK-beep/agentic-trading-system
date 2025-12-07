"""
Risk Management Agent: Position sizing, stop-loss, exposure limits.
"""
from typing import Dict

class RiskManagementAgent:
    def __init__(self):
        self.max_position = 1000
        self.max_drawdown = 0.1
    
    def approve_trade(self, proposal: Dict, portfolio: Dict) -> Dict:
        """
        Returns: {'approved': True/False, 'max_size': float, 'reason': str}
        """
        raise NotImplementedError

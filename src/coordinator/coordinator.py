from typing import Dict

from src.core.engine import TradingEngine
from src.data.loader import DataLoader
from src.agents.market_agent import MarketAnalysisAgent
from src.agents.risk_agent import RiskManagementAgent
from src.agents.execution_agent import ExecutionAgent


class Coordinator:
    def __init__(self, data_path: str, starting_cash: float = 100_000.0):
        self.loader = DataLoader(data_path)
        self.df = self.loader.load_csv()

        self.engine = TradingEngine(starting_cash=starting_cash)

        self.market_agent = MarketAnalysisAgent(self.df, short_window=5, long_window=20)
        self.risk_agent = RiskManagementAgent()
        self.execution_agent = ExecutionAgent()

    def run_step(self, index: int) -> Dict:
        market_state = self.loader.get_current_state(index)
        proposal = self.market_agent.analyze(market_state)

        decision = self.risk_agent.approve_trade(
            proposal,
            {
                "cash": self.engine.cash,
                "position": self.engine.position,
            },
        )

        orders = self.execution_agent.build_orders(decision, market_state)

        # Place and execute orders
        self.engine.place_and_execute_orders(orders, timestamp=index)

        snapshot = self.engine.step(market_state)
        snapshot["proposal"] = proposal
        snapshot["risk_decision"] = decision
        snapshot["orders"] = orders

        # THIS was missing
        return snapshot

    def run_backtest(self, start_index: int = 0, end_index: int | None = None) -> list[dict]:
        """
        Run a full backtest from start_index to end_index (exclusive).

        Returns a list of snapshots (one per time step).
        Any step that raises an error or returns None is skipped, but logged.
        """
        if end_index is None:
            end_index = len(self.df)

        results: list[dict] = []

        for i in range(start_index, end_index):
            try:
                snapshot = self.run_step(i)
                if snapshot is None:
                    print(f"[warn] run_step({i}) returned None, skipping.")
                    continue
                results.append(snapshot)
            except Exception as e:
                print(f"[error] Exception at step {i}: {e}")
                continue

        return results

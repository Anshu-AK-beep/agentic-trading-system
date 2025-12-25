from typing import List, Dict
import math
import numpy as np


def compute_metrics(backtest_results: List[Dict]) -> Dict:
    """
    Compute comprehensive performance metrics from backtest snapshots.
    """
    if not backtest_results:
        return {
            "start_value": 0.0,
            "end_value": 0.0,
            "pnl": 0.0,
            "return_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "volatility": 0.0,
            "win_rate": 0.0,
        }

    values = [s["portfolio_value"] for s in backtest_results]
    start_value = values[0]
    end_value = values[-1]
    pnl = end_value - start_value
    return_pct = (pnl / start_value) * 100 if start_value != 0 else 0.0

    # Calculate returns
    returns = []
    for i in range(1, len(values)):
        if values[i-1] != 0:
            ret = (values[i] - values[i-1]) / values[i-1]
            returns.append(ret)
    
    # Max drawdown
    peak = values[0]
    max_dd = 0.0
    for v in values:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak != 0 else 0.0
        max_dd = max(max_dd, dd)
    max_drawdown_pct = max_dd * 100

    # Volatility (annualized for daily data)
    volatility = np.std(returns) * math.sqrt(252) if returns else 0.0
    
    # Sharpe Ratio (assuming 0% risk-free rate for simplicity)
    avg_return = np.mean(returns) if returns else 0.0
    sharpe_ratio = (avg_return * math.sqrt(252) / volatility) if volatility != 0 else 0.0
    
    # Sortino Ratio (downside deviation)
    downside_returns = [r for r in returns if r < 0]
    downside_std = np.std(downside_returns) if downside_returns else 0.0
    sortino_ratio = (avg_return * math.sqrt(252) / downside_std) if downside_std != 0 else 0.0
    
    # Win rate from returns
    positive_returns = [r for r in returns if r > 0]
    win_rate = (len(positive_returns) / len(returns) * 100) if returns else 0.0

    return {
        "start_value": start_value,
        "end_value": end_value,
        "pnl": pnl,
        "return_pct": return_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "sharpe_ratio": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
        "volatility": volatility * 100,  # as percentage
        "win_rate": win_rate,
        "total_steps": len(backtest_results),
        "avg_return": avg_return * 100,  # as percentage
    }


def count_trades(backtest_results: list[dict]) -> dict:
    """
    Count and analyze trades from backtest results.
    """
    total_trades = 0
    buy_trades = 0
    sell_trades = 0
    total_volume = 0.0
    
    for s in backtest_results:
        for o in s.get("orders", []):
            total_trades += 1
            if o.get("side") == "buy":
                buy_trades += 1
            elif o.get("side") == "sell":
                sell_trades += 1
            total_volume += o.get("quantity", 0) * o.get("price", 0)
    
    return {
        "total_trades": total_trades,
        "buy_trades": buy_trades,
        "sell_trades": sell_trades,
        "total_volume": total_volume,
        "avg_trade_size": total_volume / total_trades if total_trades > 0 else 0,
    }


def calculate_agent_stats(backtest_results: list[dict]) -> dict:
    """
    Calculate statistics about agent decisions.
    """
    total_decisions = len(backtest_results)
    buy_signals = 0
    sell_signals = 0
    hold_signals = 0
    approved_trades = 0
    rejected_trades = 0
    
    for s in backtest_results:
        action = s.get("proposal", {}).get("action", "hold")
        if action == "buy":
            buy_signals += 1
        elif action == "sell":
            sell_signals += 1
        else:
            hold_signals += 1
        
        if s.get("risk_decision", {}).get("approved", False):
            approved_trades += 1
        else:
            rejected_trades += 1
    
    approval_rate = (approved_trades / total_decisions * 100) if total_decisions > 0 else 0
    
    return {
        "total_decisions": total_decisions,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "hold_signals": hold_signals,
        "approved_trades": approved_trades,
        "rejected_trades": rejected_trades,
        "approval_rate": approval_rate,
        "signal_distribution": {
            "buy_pct": (buy_signals / total_decisions * 100) if total_decisions > 0 else 0,
            "sell_pct": (sell_signals / total_decisions * 100) if total_decisions > 0 else 0,
            "hold_pct": (hold_signals / total_decisions * 100) if total_decisions > 0 else 0,
        }
    }
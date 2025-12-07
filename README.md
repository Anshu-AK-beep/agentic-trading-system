# Agentic Multi-Agent Trading System

A Python-based multi-agent trading simulator with separate agents for
market analysis, risk management, execution, and anomaly detection,
running on a custom limit order-book engine using historical market data.

## Goals

- Simulate a single-asset market using historical OHLCV data.
- Implement a custom limit order-book and basic matching logic.
- Design 4 agents:
  - Market Analysis Agent
  - Risk Management Agent
  - Execution Agent
  - Anomaly/Fraud Agent
- Coordinate agents via a central coordinator on each time step.
- Evaluate performance (PnL, drawdown, basic risk metrics).

## Tech Stack (initial)

- Python 3.10+
- pandas, numpy
- matplotlib (for PnL plots)

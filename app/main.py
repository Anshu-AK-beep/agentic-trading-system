from typing import Optional
from src.core.metrics import compute_metrics

from fastapi import FastAPI
from pydantic import BaseModel

from src.coordinator.coordinator import Coordinator

# Initialize FastAPI app
app = FastAPI(title="Agentic Trading System API")

# Global coordinator for now (simple design)
coord: Optional[Coordinator] = None


class BacktestRequest(BaseModel):
    start_index: int = 0
    end_index: Optional[int] = None
    starting_cash: float = 100_000.0


@app.on_event("startup")
def startup_event():
    global coord
    # Initialize once with default data path
    coord = Coordinator("data/raw/aapl_1y.csv", starting_cash=100_000.0)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/backtest")
def run_backtest(req: BacktestRequest):
    global coord
    if coord is None:
        coord = Coordinator("data/raw/aapl_1y.csv", starting_cash=req.starting_cash)

    if coord.engine.cash != req.starting_cash:
        coord = Coordinator("data/raw/aapl_1y.csv", starting_cash=req.starting_cash)

    results = coord.run_backtest(start_index=req.start_index, end_index=req.end_index)
    metrics = compute_metrics(results)

    return {
        "steps": len(results),
        "results": results,
        "metrics": metrics,
    }


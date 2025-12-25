import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from src.coordinator.coordinator import Coordinator
from src.core.metrics import compute_metrics, count_trades


@st.cache_resource
def get_coordinator(starting_cash: float) -> Coordinator:
    return Coordinator("data/raw/aapl_1y.csv", starting_cash=starting_cash)


st.title("Overview & Demo")

st.sidebar.header("Backtest Settings")
starting_cash = st.sidebar.number_input("Starting Cash", value=100_000.0, step=10_000.0, min_value=1_000.0)
start_index = st.sidebar.number_input("Start Index", value=30, min_value=0)
end_index = st.sidebar.number_input("End Index (exclusive)", value=200, min_value=1)

if st.sidebar.button("Run Backtest"):
    coord = get_coordinator(starting_cash)

    with st.spinner("Running backtest..."):
        results = coord.run_backtest(start_index=int(start_index), end_index=int(end_index))

    if not results:
        st.error("No results returned. Check index range.")
    else:
        df = pd.DataFrame(results)
        df["action"] = df["proposal"].apply(lambda p: p.get("action"))
        df["approved"] = df["risk_decision"].apply(lambda r: r.get("approved"))
        df["max_size"] = df["risk_decision"].apply(lambda r: r.get("max_size"))

        metrics = compute_metrics(results)
        trades = count_trades(results)

        tab1, tab2, tab3 = st.tabs(["Summary", "Charts", "Agent Decisions"])

        with tab1:
            st.subheader("Performance Metrics")
            c1, c2, c3 = st.columns(3)
            c1.metric("Start Value", f"{metrics['start_value']:.2f}")
            c2.metric("End Value", f"{metrics['end_value']:.2f}")
            c3.metric("PnL", f"{metrics['pnl']:.2f}")

            c4, c5, c6 = st.columns(3)
            c4.metric("Return %", f"{metrics['return_pct']:.2f}%")
            c5.metric("Max Drawdown %", f"{metrics['max_drawdown_pct']:.2f}%")
            c6.metric("Total Trades", f"{trades['total_trades']}")

        with tab2:
            st.subheader("Portfolio Value Over Time")
            st.line_chart(df.set_index("step")["portfolio_value"])

            st.subheader("Cash and Position")
            st.line_chart(df.set_index("step")[["cash", "position"]])

        with tab3:
            st.subheader("Agent Decisions (first 30 steps)")
            st.dataframe(
                df[["step", "price", "action", "approved", "max_size", "orders"]].head(30)
            )
else:
    st.info("Set parameters on the left and click 'Run Backtest'.")

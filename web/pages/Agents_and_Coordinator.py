import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Agents & Coordinator", page_icon="🤖", layout="wide")

st.title("🤖 Agents & Coordinator")
st.markdown("Inspect agent decisions and coordinator actions at each time step")

# Check if backtest results exist in session state
if st.session_state.get('backtest_results') is not None:
    results = st.session_state.backtest_results
    df = st.session_state.backtest_df
    
    st.success(f"✅ Showing results from latest backtest ({len(results)} steps)")
    
    # Step selector
    step = st.slider(
        "Select Step to Inspect",
        min_value=int(df['step'].min()),
        max_value=int(df['step'].max()),
        value=int(df['step'].min() + 10)
    )
    
    # Find the snapshot for this step
    snap = None
    for s in results:
        if s['step'] == step:
            snap = s
            break
    
    if snap:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### 📊 Step {snap['step']} – Market State")
            
            market_col1, market_col2, market_col3 = st.columns(3)
            with market_col1:
                st.metric("Price", f"${snap['price']:.2f}")
            with market_col2:
                st.metric("Cash", f"${snap['cash']:,.2f}")
            with market_col3:
                st.metric("Position", f"{snap['position']:.2f} shares")
            
            st.markdown("---")
            
            # Agent decisions in cards
            st.markdown("### 🧠 Market Analysis Agent")
            proposal = snap['proposal']
            
            action_emoji = {"buy": "📈", "sell": "📉", "hold": "⏸️"}
            action_color = {"buy": "#48bb78", "sell": "#ed8936", "hold": "#718096"}
            
            st.markdown(f"""
            <div style="background: {action_color.get(proposal.get('action', 'hold'), '#718096')}; 
                        color: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                <h4>{action_emoji.get(proposal.get('action', 'hold'), '⏸️')} 
                    Action: {proposal.get('action', 'hold').upper()}</h4>
                <p>Confidence: {proposal.get('confidence', 0):.1%}</p>
                <p>Target Price: ${proposal.get('target_price', 0):.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🛡️ Risk Management Agent")
            decision = snap['risk_decision']
            
            if decision.get('approved', False):
                st.success(f"✅ **APPROVED** - {decision.get('reason', 'Unknown')}")
                st.info(f"Max Trade Size: {decision.get('max_size', 0):.2f} shares")
            else:
                st.error(f"❌ **REJECTED** - {decision.get('reason', 'Unknown')}")
            
            st.markdown("### ⚡ Execution Agent")
            orders = snap['orders']
            
            if orders:
                for idx, order in enumerate(orders):
                    st.markdown(f"""
                    **Order #{idx+1}**
                    - Side: {order['side'].upper()}
                    - Price: ${order['price']:.2f}
                    - Quantity: {order['quantity']:.2f} shares
                    """)
            else:
                st.info("No orders executed at this step")
        
        with col2:
            st.markdown("### 📈 Portfolio Value")
            st.metric(
                "Total Value",
                f"${snap['portfolio_value']:,.2f}",
                delta=None
            )
            
            st.markdown("### 🔄 Agent Flow")
            st.markdown("""
            ```
            1. Market Agent
               ↓ Signal
            2. Risk Agent
               ↓ Approval
            3. Execution Agent
               ↓ Orders
            4. Order Book
               ↓ Trades
            5. Portfolio Update
            ```
            """)
            
            st.markdown("### 📊 Step Statistics")
            st.json({
                "step": snap['step'],
                "action": proposal.get('action'),
                "approved": decision.get('approved'),
                "orders_count": len(orders),
                "cash": f"${snap['cash']:,.2f}",
                "position": f"{snap['position']:.2f}",
                "portfolio_value": f"${snap['portfolio_value']:,.2f}"
            })
    
    # Show timeline of all steps
    st.markdown("---")
    st.markdown("### 📅 Timeline of All Steps")
    
    timeline_df = df[['step', 'price', 'action', 'approved', 'cash', 'position', 'portfolio_value']].copy()
    st.dataframe(timeline_df, use_container_width=True, height=400)
    
else:
    st.warning("⚠️ No backtest results found. Run a backtest from the main page first!")
    st.info("💡 Go to the **app** page and click 'Run Backtest' to generate data.")
    
    st.markdown("---")
    st.markdown("### 🔍 What You'll See Here")
    st.markdown("""
    Once you run a backtest, this page will show:
    
    - **Step-by-step analysis** of agent decisions
    - **Market state** at each time point
    - **Agent proposals** and risk assessments
    - **Order execution** details
    - **Portfolio changes** over time
    
    Navigate back to the main page to start!
    """)
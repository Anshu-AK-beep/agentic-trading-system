import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Engine & OrderBook", page_icon="🔧", layout="wide")

st.title("🔧 Engine & Order Book Details")
st.markdown("Inspect order execution and order book state")

# Check if backtest results exist
if st.session_state.get('backtest_results') is not None:
    results = st.session_state.backtest_results
    df = st.session_state.backtest_df
    
    st.success(f"✅ Showing results from latest backtest ({len(results)} steps)")
    
    # Range selector for detailed inspection
    st.markdown("### 📊 Select Range for Detailed Inspection")
    
    col1, col2 = st.columns(2)
    with col1:
        start_step = st.number_input(
            "Start Step",
            min_value=int(df['step'].min()),
            max_value=int(df['step'].max()),
            value=int(df['step'].min())
        )
    with col2:
        end_step = st.number_input(
            "End Step",
            min_value=int(df['step'].min()),
            max_value=int(df['step'].max()),
            value=min(int(df['step'].min()) + 20, int(df['step'].max()))
        )
    
    # Filter results for selected range
    filtered_results = [r for r in results if start_step <= r['step'] <= end_step]
    filtered_df = df[(df['step'] >= start_step) & (df['step'] <= end_step)]
    
    if filtered_results:
        st.markdown(f"### 📈 Order Execution Timeline (Steps {start_step} to {end_step})")
        
        # Create visualization
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=filtered_df['step'],
            y=filtered_df['price'],
            mode='lines',
            name='Price',
            line=dict(color='#667eea', width=2)
        ))
        
        # Add buy/sell markers
        buy_steps = filtered_df[filtered_df['action'] == 'buy']
        sell_steps = filtered_df[filtered_df['action'] == 'sell']
        
        if not buy_steps.empty:
            fig.add_trace(go.Scatter(
                x=buy_steps['step'],
                y=buy_steps['price'],
                mode='markers',
                name='Buy Orders',
                marker=dict(color='#48bb78', size=12, symbol='triangle-up')
            ))
        
        if not sell_steps.empty:
            fig.add_trace(go.Scatter(
                x=sell_steps['step'],
                y=sell_steps['price'],
                mode='markers',
                name='Sell Orders',
                marker=dict(color='#ed8936', size=12, symbol='triangle-down')
            ))
        
        fig.update_layout(
            title="Price and Order Execution",
            xaxis_title="Step",
            yaxis_title="Price ($)",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed order table
        st.markdown("### 📋 Order Details")
        
        order_data = []
        for r in filtered_results:
            for order in r.get('orders', []):
                order_data.append({
                    'Step': r['step'],
                    'Side': order['side'].upper(),
                    'Price': f"${order['price']:.2f}",
                    'Quantity': f"{order['quantity']:.2f}",
                    'Value': f"${order['price'] * order['quantity']:,.2f}"
                })
        
        if order_data:
            order_df = pd.DataFrame(order_data)
            st.dataframe(order_df, use_container_width=True)
            
            # Summary statistics
            st.markdown("### 📊 Range Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_orders = len(order_data)
                st.metric("Total Orders", total_orders)
            
            with col2:
                buy_orders = len([o for o in order_data if o['Side'] == 'BUY'])
                st.metric("Buy Orders", buy_orders)
            
            with col3:
                sell_orders = len([o for o in order_data if o['Side'] == 'SELL'])
                st.metric("Sell Orders", sell_orders)
            
            with col4:
                total_volume = sum([o['quantity'] for r in filtered_results for o in r.get('orders', [])])
                st.metric("Total Volume", f"{total_volume:.2f}")
        else:
            st.info("No orders executed in this range")
        
        # Position and cash flow
        st.markdown("### 💰 Position & Cash Flow")
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=filtered_df['step'],
            y=filtered_df['cash'],
            mode='lines',
            name='Cash',
            line=dict(color='#48bb78', width=2),
            yaxis='y'
        ))
        
        fig2.add_trace(go.Scatter(
            x=filtered_df['step'],
            y=filtered_df['position'],
            mode='lines',
            name='Position',
            line=dict(color='#ed8936', width=2),
            yaxis='y2'
        ))
        
        fig2.update_layout(
            title="Cash and Position Over Time",
            xaxis_title="Step",
            yaxis_title="Cash ($)",
            yaxis2=dict(
                title="Position (shares)",
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Engine state changes
        st.markdown("### 🔄 Engine State Changes")
        state_df = filtered_df[['step', 'price', 'cash', 'position', 'portfolio_value']].copy()
        state_df['cash'] = state_df['cash'].apply(lambda x: f"${x:,.2f}")
        state_df['position'] = state_df['position'].apply(lambda x: f"{x:.2f}")
        state_df['portfolio_value'] = state_df['portfolio_value'].apply(lambda x: f"${x:,.2f}")
        state_df['price'] = state_df['price'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(state_df, use_container_width=True, height=300)
    
else:
    st.warning("⚠️ No backtest results found. Run a backtest from the main page first!")
    st.info("💡 Go to the **app** page and click 'Run Backtest' to generate data.")
    
    st.markdown("---")
    st.markdown("### 🔍 What You'll See Here")
    st.markdown("""
    Once you run a backtest, this page will show:
    
    - **Order execution timeline** with buy/sell markers
    - **Order book state** at each step
    - **Position and cash flow** tracking
    - **Trade-by-trade details** with prices and quantities
    - **Engine state changes** over time
    
    Navigate back to the main page to start!
    """)
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Metrics & Analysis", page_icon="📊", layout="wide")

st.title("📊 Metrics & Analysis")
st.markdown("Comprehensive performance metrics and statistical analysis")

# Check if backtest results exist
if st.session_state.get('backtest_results') is not None:
    results = st.session_state.backtest_results
    df = st.session_state.backtest_df
    metrics = st.session_state.metrics
    trades = st.session_state.trades
    
    st.success(f"✅ Analyzing {len(results)} steps of backtest data")
    
    # Main metrics dashboard
    st.markdown("### 📈 Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Starting Value",
            f"${metrics['start_value']:,.2f}",
            help="Initial portfolio value"
        )
    
    with col2:
        st.metric(
            "Ending Value",
            f"${metrics['end_value']:,.2f}",
            f"{metrics['pnl']:+,.2f}",
            help="Final portfolio value and PnL"
        )
    
    with col3:
        st.metric(
            "Total Return",
            f"{metrics['return_pct']:.2f}%",
            delta_color="normal",
            help="Percentage return on investment"
        )
    
    with col4:
        st.metric(
            "Max Drawdown",
            f"{metrics['max_drawdown_pct']:.2f}%",
            delta_color="inverse",
            help="Maximum peak-to-trough decline"
        )
    
    st.markdown("---")
    
    # Additional metrics
    st.markdown("### 📊 Detailed Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Trading Activity")
        st.metric("Total Trades", trades['total_trades'])
        st.metric("Buy Trades", trades['buy_trades'])
        st.metric("Sell Trades", trades['sell_trades'])
        
        if trades['total_trades'] > 0:
            win_rate = (trades['buy_trades'] / trades['total_trades']) * 100
            st.metric("Buy Rate", f"{win_rate:.1f}%")
    
    with col2:
        st.markdown("#### Portfolio Metrics")
        
        # Calculate additional metrics
        total_steps = len(results)
        active_trades = len([r for r in results if len(r.get('orders', [])) > 0])
        
        st.metric("Total Steps", total_steps)
        st.metric("Active Steps", active_trades)
        st.metric("Activity Rate", f"{(active_trades/total_steps*100):.1f}%")
    
    with col3:
        st.markdown("#### Risk Metrics")
        st.metric("Max Drawdown", f"{metrics['max_drawdown_pct']:.2f}%")
        
        # Calculate volatility from returns
        values = df['portfolio_value'].values
        returns = [(values[i] - values[i-1])/values[i-1] for i in range(1, len(values))]
        volatility = pd.Series(returns).std() * 100
        
        st.metric("Volatility", f"{volatility:.2f}%")
        
        # Sharpe-like ratio (simplified)
        if volatility > 0:
            sharpe = (metrics['return_pct'] / total_steps) / (volatility / 100)
            st.metric("Risk-Adj Return", f"{sharpe:.2f}")
    
    # Visualizations
    st.markdown("---")
    st.markdown("### 📈 Performance Visualizations")
    
    # Create comprehensive chart
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Portfolio Value Over Time',
            'Drawdown Analysis',
            'Returns Distribution',
            'Trade Frequency',
            'Cash vs Position',
            'Cumulative Returns'
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"type": "histogram"}, {"type": "bar"}],
            [{"secondary_y": False}, {"secondary_y": False}]
        ],
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    # 1. Portfolio value
    fig.add_trace(
        go.Scatter(
            x=df['step'],
            y=df['portfolio_value'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#667eea', width=2),
            fill='tozeroy'
        ),
        row=1, col=1
    )
    
    # 2. Drawdown
    portfolio_values = df['portfolio_value'].values
    running_max = pd.Series(portfolio_values).expanding().max()
    drawdown = (portfolio_values - running_max) / running_max * 100
    
    fig.add_trace(
        go.Scatter(
            x=df['step'],
            y=drawdown,
            mode='lines',
            name='Drawdown',
            line=dict(color='#ed8936', width=2),
            fill='tozeroy'
        ),
        row=1, col=2
    )
    
    # 3. Returns distribution
    fig.add_trace(
        go.Histogram(
            x=returns,
            name='Returns',
            marker_color='#48bb78',
            nbinsx=30
        ),
        row=2, col=1
    )
    
    # 4. Trade frequency
    action_counts = df['action'].value_counts()
    fig.add_trace(
        go.Bar(
            x=action_counts.index,
            y=action_counts.values,
            name='Actions',
            marker_color=['#48bb78', '#ed8936', '#718096']
        ),
        row=2, col=2
    )
    
    # 5. Cash vs Position
    fig.add_trace(
        go.Scatter(
            x=df['step'],
            y=df['cash'],
            mode='lines',
            name='Cash',
            line=dict(color='#48bb78', width=2)
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['step'],
            y=df['position'] * df['price'],  # Position value in dollars
            mode='lines',
            name='Position Value',
            line=dict(color='#ed8936', width=2)
        ),
        row=3, col=1
    )
    
    # 6. Cumulative returns
    cumulative_returns = [(v - metrics['start_value']) / metrics['start_value'] * 100 
                          for v in portfolio_values]
    
    fig.add_trace(
        go.Scatter(
            x=df['step'],
            y=cumulative_returns,
            mode='lines',
            name='Cumulative Return',
            line=dict(color='#9f7aea', width=2),
            fill='tozeroy'
        ),
        row=3, col=2
    )
    
    fig.update_layout(
        height=1000,
        showlegend=False,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Agent performance analysis
    st.markdown("---")
    st.markdown("### 🤖 Agent Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Decision Distribution")
        
        action_dist = df['action'].value_counts()
        approval_dist = df['approved'].value_counts()
        
        fig_agents = go.Figure()
        
        fig_agents.add_trace(go.Bar(
            name='Actions',
            x=action_dist.index,
            y=action_dist.values,
            marker_color='#667eea'
        ))
        
        fig_agents.update_layout(
            title="Agent Actions Distribution",
            xaxis_title="Action",
            yaxis_title="Count",
            template='plotly_white',
            height=300
        )
        
        st.plotly_chart(fig_agents, use_container_width=True)
    
    with col2:
        st.markdown("#### Approval Rate Over Time")
        
        approval_rate = df.groupby('step')['approved'].mean().rolling(10).mean() * 100
        
        fig_approval = go.Figure()
        
        fig_approval.add_trace(go.Scatter(
            x=df['step'],
            y=approval_rate,
            mode='lines',
            name='Approval Rate',
            line=dict(color='#48bb78', width=2),
            fill='tozeroy'
        ))
        
        fig_approval.update_layout(
            title="Risk Agent Approval Rate (10-step MA)",
            xaxis_title="Step",
            yaxis_title="Approval Rate (%)",
            template='plotly_white',
            height=300
        )
        
        st.plotly_chart(fig_approval, use_container_width=True)
    
    # Statistical summary
    st.markdown("---")
    st.markdown("### 📋 Statistical Summary")
    
    summary_data = {
        "Metric": [
            "Total Steps",
            "Starting Value",
            "Ending Value",
            "Total PnL",
            "Return %",
            "Max Drawdown %",
            "Total Trades",
            "Buy Trades",
            "Sell Trades",
            "Hold Actions",
            "Avg Portfolio Value",
            "Volatility %"
        ],
        "Value": [
            f"{len(results)}",
            f"${metrics['start_value']:,.2f}",
            f"${metrics['end_value']:,.2f}",
            f"${metrics['pnl']:+,.2f}",
            f"{metrics['return_pct']:.2f}%",
            f"{metrics['max_drawdown_pct']:.2f}%",
            f"{trades['total_trades']}",
            f"{trades['buy_trades']}",
            f"{trades['sell_trades']}",
            f"{len(df[df['action'] == 'hold'])}",
            f"${df['portfolio_value'].mean():,.2f}",
            f"{volatility:.2f}%"
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Export option
    st.markdown("---")
    st.markdown("### 💾 Export Data")
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="backtest_results.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    st.warning("⚠️ No backtest results found. Run a backtest from the main page first!")
    st.info("💡 Go to the **app** page and click 'Run Backtest' to generate data.")
    
    st.markdown("---")
    st.markdown("### 🔍 What You'll See Here")
    st.markdown("""
    Once you run a backtest, this page will show:
    
    - **Comprehensive metrics**: PnL, returns, drawdown, volatility, Sharpe ratio
    - **Performance visualizations**: 6 different charts analyzing your backtest
    - **Agent performance**: Decision distribution and approval rates
    - **Statistical summary**: Complete breakdown of all metrics
    - **Data export**: Download results as CSV for further analysis
    
    Navigate back to the main page to start!
    """)
import sys
from pathlib import Path

# Add project root to Python path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.coordinator.coordinator import Coordinator
from src.core.metrics import compute_metrics, count_trades

# Page config
st.set_page_config(
    page_title="Agentic Trading System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing results
if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = None
if 'backtest_df' not in st.session_state:
    st.session_state.backtest_df = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None
if 'trades' not in st.session_state:
    st.session_state.trades = None

# Custom CSS for modern look
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stMetric label {
        color: white !important;
        font-weight: 600;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2rem;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    .project-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    .agent-card {
        background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .agent-card:hover {
        transform: translateX(5px);
    }
    .agent-card h4 {
        color: #667eea;
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }
    .agent-card p {
        color: #4a5568;
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .feature-badge {
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.2rem;
    }
    .info-box {
        background: #ebf4ff;
        border-left: 4px solid #3182ce;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="project-header">
    <h1>🤖 Agentic Trading System</h1>
    <p style="font-size: 1.2rem; margin-top: 1rem; opacity: 0.95;">
        A Python-based multi-agent trading simulator powered by autonomous AI agents 
        working together to analyze markets, manage risk, and execute trades on a 
        custom limit order book engine using real historical market data.
    </p>
</div>
""", unsafe_allow_html=True)

# Overview Tabs
tab1, tab2, tab3 = st.tabs(["📚 Project Overview", "🚀 Live Demo", "🔍 How It Works"])

with tab1:
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 🎯 Project Goals")
        st.markdown("""
        - **Simulate** a single-asset market using historical OHLCV data
        - **Implement** a custom limit order book with efficient matching logic
        - **Coordinate** multiple specialized AI agents for different trading tasks
        - **Evaluate** performance with comprehensive metrics (PnL, drawdown, Sharpe ratio)
        - **Visualize** agent decisions and market dynamics in real-time
        """)
        
        st.markdown("### 🏗️ Architecture")
        st.markdown("""
        The system uses a **multi-agent architecture** where specialized agents 
        collaborate to make trading decisions:
        """)
        
        # Fixed agent cards with proper HTML rendering
        st.markdown("""
        <div class="agent-card">
            <h4>🧠 Market Analysis Agent</h4>
            <p>Analyzes price patterns using technical indicators (SMA crossover) to generate buy/sell/hold signals</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <h4>🛡️ Risk Management Agent</h4>
            <p>Controls position sizing and enforces risk limits to protect capital</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <h4>⚡ Execution Agent</h4>
            <p>Converts approved decisions into concrete orders and submits them to the order book</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <h4>🔍 Anomaly Detection Agent</h4>
            <p>Monitors for unusual market behavior and potential fraud (coming soon)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💻 Tech Stack")
        tech_stack = {
            "Core": ["Python 3.10+", "FastAPI", "Streamlit"],
            "Data": ["pandas", "numpy", "yfinance"],
            "Visualization": ["plotly", "matplotlib"],
            "Performance": ["sortedcontainers", "caching"]
        }
        
        for category, techs in tech_stack.items():
            st.markdown(f"**{category}**")
            for tech in techs:
                st.markdown(f'<span class="feature-badge">{tech}</span>', unsafe_allow_html=True)
            st.markdown("")
        
        st.markdown("### 📊 Key Features")
        features = [
            "Real-time order book visualization",
            "Multi-agent coordination system",
            "Historical data backtesting",
            "Performance metrics dashboard",
            "Customizable trading strategies",
            "Risk-adjusted position sizing"
        ]
        for feature in features:
            st.markdown(f"✅ {feature}")

with tab2:
    st.markdown("### 🚀 Run a Live Backtest")
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        starting_cash = st.number_input(
            "💰 Starting Capital ($)",
            value=100_000.0,
            step=10_000.0,
            min_value=1_000.0,
            help="Initial cash balance for trading"
        )
        
        st.markdown("---")
        st.markdown("### 📅 Backtest Period")
        
        start_index = st.number_input(
            "Start Index",
            value=30,
            min_value=0,
            help="Starting time step (need 30+ for SMA calculation)"
        )
        
        end_index = st.number_input(
            "End Index",
            value=200,
            min_value=1,
            help="Ending time step (exclusive)"
        )
        
        st.markdown("---")
        
        # Show navigation hint if results exist
        if st.session_state.backtest_results is not None:
            st.success("✅ Backtest Complete!")
            st.markdown("### 📊 View Detailed Results")
            st.info("""
            Navigate to other pages to see:
            - **Agents & Coordinator**: Agent decisions per step
            - **Engine & OrderBook**: Order execution details
            - **Metrics & Analysis**: Performance breakdown
            """)
    
    # Main demo area
    if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
        with st.spinner("🔄 Running simulation..."):
            try:
                # Initialize coordinator
                coord = Coordinator("data/raw/aapl_1y.csv", starting_cash=starting_cash)
                
                # Run backtest
                results = coord.run_backtest(start_index=int(start_index), end_index=int(end_index))
                
                if not results:
                    st.error("❌ No results returned. Check your index range.")
                else:
                    # Store results in session state for other pages
                    st.session_state.backtest_results = results
                    
                    # Process results
                    df = pd.DataFrame(results)
                    df["action"] = df["proposal"].apply(lambda p: p.get("action"))
                    df["approved"] = df["risk_decision"].apply(lambda r: r.get("approved"))
                    df["max_size"] = df["risk_decision"].apply(lambda r: r.get("max_size"))
                    
                    st.session_state.backtest_df = df
                    
                    metrics = compute_metrics(results)
                    trades = count_trades(results)
                    
                    st.session_state.metrics = metrics
                    st.session_state.trades = trades
                    
                    # Metrics Dashboard
                    st.markdown("### 📊 Performance Metrics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "💵 Final Value",
                            f"${metrics['end_value']:,.2f}",
                            f"{metrics['pnl']:+,.2f}"
                        )
                    
                    with col2:
                        st.metric(
                            "📈 Total Return",
                            f"{metrics['return_pct']:.2f}%",
                            delta_color="normal"
                        )
                    
                    with col3:
                        st.metric(
                            "📉 Max Drawdown",
                            f"{metrics['max_drawdown_pct']:.2f}%",
                            delta_color="inverse"
                        )
                    
                    with col4:
                        st.metric(
                            "🔄 Total Trades",
                            f"{trades['total_trades']}",
                            f"Buy: {trades['buy_trades']} | Sell: {trades['sell_trades']}"
                        )
                    
                    # Charts
                    st.markdown("---")
                    st.markdown("### 📈 Portfolio Performance")
                    
                    # Create subplot figure
                    fig = make_subplots(
                        rows=2, cols=2,
                        subplot_titles=('Portfolio Value Over Time', 'Cash & Position', 
                                      'Trade Distribution', 'Agent Activity'),
                        specs=[[{"secondary_y": False}, {"secondary_y": False}],
                               [{"type": "bar"}, {"type": "scatter"}]],
                        vertical_spacing=0.12,
                        horizontal_spacing=0.1
                    )
                    
                    # Portfolio value
                    fig.add_trace(
                        go.Scatter(
                            x=df['step'],
                            y=df['portfolio_value'],
                            mode='lines',
                            name='Portfolio Value',
                            line=dict(color='#667eea', width=2),
                            fill='tozeroy',
                            fillcolor='rgba(102, 126, 234, 0.1)'
                        ),
                        row=1, col=1
                    )
                    
                    # Cash and position
                    fig.add_trace(
                        go.Scatter(
                            x=df['step'],
                            y=df['cash'],
                            mode='lines',
                            name='Cash',
                            line=dict(color='#48bb78', width=2)
                        ),
                        row=1, col=2
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=df['step'],
                            y=df['position'],
                            mode='lines',
                            name='Position',
                            line=dict(color='#ed8936', width=2)
                        ),
                        row=1, col=2
                    )
                    
                    # Trade distribution
                    action_counts = df['action'].value_counts()
                    fig.add_trace(
                        go.Bar(
                            x=action_counts.index,
                            y=action_counts.values,
                            name='Actions',
                            marker_color=['#48bb78', '#ed8936', '#718096']
                        ),
                        row=2, col=1
                    )
                    
                    # Agent approval rate
                    approval_rate = df.groupby('step')['approved'].mean().rolling(10).mean()
                    fig.add_trace(
                        go.Scatter(
                            x=df['step'],
                            y=approval_rate,
                            mode='lines',
                            name='Approval Rate',
                            line=dict(color='#9f7aea', width=2)
                        ),
                        row=2, col=2
                    )
                    
                    fig.update_layout(
                        height=700,
                        showlegend=True,
                        template='plotly_white',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Success message with navigation
                    st.success("✅ Backtest completed successfully!")
                    st.info("💡 **Navigate to other pages** (left sidebar) to explore detailed results for agents, order book, and metrics!")
                    
                    # Detailed data
                    with st.expander("📋 View Detailed Results"):
                        st.dataframe(
                            df[['step', 'price', 'action', 'approved', 'max_size', 
                                'cash', 'position', 'portfolio_value']],
                            use_container_width=True
                        )
            except Exception as e:
                st.error(f"❌ Error running backtest: {str(e)}")
                st.error("Make sure the data file exists at: data/raw/aapl_1y.csv")
    else:
        st.info("👆 Configure your backtest settings in the sidebar and click 'Run Backtest' to begin!")
        
        # Show sample visualization
        st.markdown("### 💡 What You'll See")
        st.markdown("""
        After running a backtest, you'll get:
        - **Real-time metrics**: PnL, returns, drawdown, trade statistics
        - **Interactive charts**: Portfolio value, cash flow, position tracking
        - **Agent insights**: See what decisions agents made at each step
        - **Performance analysis**: Detailed breakdown of trading activity
        
        Results will be available in all pages for detailed analysis!
        """)

with tab3:
    st.markdown("### 🔍 System Architecture & Workflow")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔄 Trading Loop")
        st.code("""
1. Load Market Data
   ↓
2. Market Agent Analyzes
   → Technical indicators
   → Generate signal (buy/sell/hold)
   ↓
3. Risk Agent Evaluates
   → Check position limits
   → Calculate position size
   → Approve or reject
   ↓
4. Execution Agent Acts
   → Create orders
   → Submit to order book
   ↓
5. Order Book Matches
   → Match buyers and sellers
   → Execute trades
   → Update positions
   ↓
6. Update Portfolio
   → Calculate PnL
   → Track metrics
   → Log activity
        """, language="text")
    
    with col2:
        st.markdown("#### 📚 Order Book Mechanics")
        st.markdown("""
        Our **custom limit order book** features:
        
        - **Price-Time Priority**: Orders matched by price, then time
        - **Efficient Matching**: O(log n) operations using sorted data structures
        - **Aggregated Levels**: Orders grouped by price level
        - **Real-time Updates**: Instant order book state after each trade
        
        #### 🧪 Strategy Details
        
        **Current Implementation**: SMA Crossover
        - Short SMA (5 periods) vs Long SMA (20 periods)
        - Buy when price > short SMA
        - Sell when price < short SMA
        - Confidence-weighted signals
        
        **Risk Management**:
        - Maximum position size limits
        - Per-trade size constraints
        - Portfolio exposure monitoring
        """)
    
    st.markdown("---")
    st.markdown("### 🎓 Educational Value")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### For Students")
        st.markdown("""
        - Learn multi-agent systems
        - Understand trading mechanics
        - Practice Python development
        - Explore financial markets
        """)
    
    with col2:
        st.markdown("#### For Developers")
        st.markdown("""
        - FastAPI backend design
        - Streamlit UI development
        - Algorithm optimization
        - System architecture
        """)
    
    with col3:
        st.markdown("#### For Traders")
        st.markdown("""
        - Backtest strategies
        - Analyze risk metrics
        - Study order flow
        - Optimize parameters
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 2rem;">
    <p>🤖 Agentic Trading System | Built with Python, FastAPI & Streamlit</p>
    <p>Navigate to other pages for detailed analysis: <b>Agents & Coordinator</b> • <b>Engine & OrderBook</b> • <b>Metrics & Analysis</b></p>
</div>
""", unsafe_allow_html=True)
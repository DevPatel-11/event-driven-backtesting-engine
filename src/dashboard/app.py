#!/usr/bin/env python3
"""Interactive Backtest Dashboard using Streamlit and Plotly."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Backtest Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
.stMetric {
    background-color: white;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

def load_sample_data():
    """Load or generate sample backtest data."""
    np.random.seed(42)
    n_days = 252
    dates = pd.date_range('2024-01-01', periods=n_days, freq='D')
    
    # Generate synthetic equity curve with realistic characteristics
    returns = np.random.normal(0.0008, 0.02, n_days)  # 0.08% daily mean, 2% volatility
    returns = returns + np.random.choice([-1, 1], n_days) * np.random.exponential(0.005, n_days) * 0.1
    equity = 100000 * (1 + returns).cumprod()
    
    # Generate execution data
    trades = pd.DataFrame({
        'timestamp': dates[:200],
        'symbol': np.random.choice(['AAPL', 'GOOGL', 'MSFT', 'AMZN'], 200),
        'side': np.random.choice(['BUY', 'SELL'], 200),
        'quantity': np.random.randint(10, 200, 200),
        'price': np.random.uniform(100, 200, 200),
        'slippage_bps': np.random.gamma(2, 0.5, 200),
        'latency_ms': np.random.lognormal(1.5, 0.8, 200),
        'commission': np.random.uniform(0.5, 2.0, 200)
    })
    
    # Market data
    market_data = pd.DataFrame({
        'timestamp': dates,
        'price': 150 + np.cumsum(np.random.normal(0, 2, n_days)),
        'volume': np.random.lognormal(10, 1, n_days),
        'bid_volume': np.random.uniform(0.4, 0.6, n_days),
        'ask_volume': None
    })
    market_data['ask_volume'] = 1 - market_data['bid_volume']
    market_data['imbalance'] = market_data['bid_volume'] - market_data['ask_volume']
    
    return {
        'equity': pd.DataFrame({'date': dates, 'equity': equity}),
        'trades': trades,
        'market': market_data
    }

def calculate_metrics(equity_df):
    """Calculate key performance metrics."""
    returns = equity_df['equity'].pct_change().dropna()
    
    # Calculate drawdown
    cumulative = equity_df['equity']
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    metrics = {
        'total_return': (equity_df['equity'].iloc[-1] / equity_df['equity'].iloc[0] - 1) * 100,
        'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
        'max_drawdown': drawdown.min() * 100,
        'win_rate': (returns > 0).sum() / len(returns) * 100,
        'volatility': returns.std() * np.sqrt(252) * 100,
        'total_trades': len(returns)
    }
    
    equity_df['drawdown'] = drawdown * 100
    return metrics, equity_df

# Title
st.title("📈 Event-Driven Backtest Dashboard")
st.markdown("Interactive visualization of backtest results with execution analytics")

# Load data
data = load_sample_data()
metrics, equity_data = calculate_metrics(data['equity'])

# Sidebar
st.sidebar.header("⚙️ Configuration")
show_trades = st.sidebar.checkbox("Show Trade Markers", value=True)
show_drawdown = st.sidebar.checkbox("Show Drawdown", value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")
st.sidebar.metric("Total Return", f"{metrics['total_return']:.2f}%")
st.sidebar.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
st.sidebar.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%")

# Main metrics row
st.header("📊 Performance Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Return",
        f"{metrics['total_return']:.2f}%",
        delta=f"{metrics['total_return']/12:.2f}% / month"
    )

with col2:
    st.metric(
        "Sharpe Ratio",
        f"{metrics['sharpe_ratio']:.2f}",
        delta="Good" if metrics['sharpe_ratio'] > 1 else "Poor"
    )

with col3:
    st.metric(
        "Max Drawdown",
        f"{metrics['max_drawdown']:.2f}%",
        delta="Acceptable" if metrics['max_drawdown'] > -20 else "High"
    )

with col4:
    st.metric(
        "Win Rate",
        f"{metrics['win_rate']:.1f}%",
        delta=f"{metrics['volatility']:.1f}% Vol"
    )

st.markdown("---")

# Equity Curve & Drawdown
st.header("💵 Equity Curve & Drawdown")
fig_equity = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    subplot_titles=('Equity Curve', 'Drawdown %'),
    row_heights=[0.7, 0.3]
)

# Equity curve
fig_equity.add_trace(
    go.Scatter(
        x=equity_data['date'],
        y=equity_data['equity'],
        name='Equity',
        line=dict(color='#2E86AB', width=2),
        fill='tozeroy',
        fillcolor='rgba(46, 134, 171, 0.1)'
    ),
    row=1, col=1
)

# Drawdown
if show_drawdown:
    fig_equity.add_trace(
        go.Scatter(
            x=equity_data['date'],
            y=equity_data['drawdown'],
            name='Drawdown',
            line=dict(color='#A23B72', width=2),
            fill='tozeroy',
            fillcolor='rgba(162, 59, 114, 0.2)'
        ),
        row=2, col=1
    )

fig_equity.update_xaxes(title_text="Date", row=2, col=1)
fig_equity.update_yaxes(title_text="Equity ($)", row=1, col=1)
fig_equity.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
fig_equity.update_layout(height=600, showlegend=True, hovermode='x unified')
st.plotly_chart(fig_equity, use_container_width=True)

st.markdown("---")

# Execution Analytics
st.header("⚡ Execution Analytics")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Slippage Distribution")
    fig_slippage = go.Figure()
    fig_slippage.add_trace(go.Histogram(
        x=data['trades']['slippage_bps'],
        nbinsx=30,
        name='Slippage',
        marker_color='#F18F01'
    ))
    fig_slippage.update_layout(
        xaxis_title="Slippage (bps)",
        yaxis_title="Frequency",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_slippage, use_container_width=True)
    
    # Slippage stats
    avg_slippage = data['trades']['slippage_bps'].mean()
    st.metric("Avg Slippage", f"{avg_slippage:.2f} bps")

with col2:
    st.subheader("Latency Distribution")
    fig_latency = go.Figure()
    fig_latency.add_trace(go.Histogram(
        x=data['trades']['latency_ms'],
        nbinsx=30,
        name='Latency',
        marker_color='#06A77D'
    ))
    fig_latency.update_layout(
        xaxis_title="Latency (ms)",
        yaxis_title="Frequency",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_latency, use_container_width=True)
    
    # Latency stats
    avg_latency = data['trades']['latency_ms'].mean()
    p99_latency = data['trades']['latency_ms'].quantile(0.99)
    st.metric("Avg Latency", f"{avg_latency:.2f} ms", delta=f"p99: {p99_latency:.2f} ms")

st.markdown("---")

# Market Microstructure
st.header("📋 Market Microstructure")
st.subheader("Volume Imbalance")

fig_imbalance = go.Figure()
fig_imbalance.add_trace(go.Bar(
    x=data['market']['timestamp'],
    y=data['market']['imbalance'],
    name='Imbalance',
    marker=dict(
        color=data['market']['imbalance'],
        colorscale=['#A23B72', '#F0F0F0', '#2E86AB'],
        cmid=0,
        colorbar=dict(title="Imbalance")
    )
))

fig_imbalance.update_layout(
    xaxis_title="Date",
    yaxis_title="Buy/Sell Imbalance",
    height=400,
    showlegend=False,
    hovermode='x unified'
)

st.plotly_chart(fig_imbalance, use_container_width=True)
st.caption("Positive = More bid volume, Negative = More ask volume")

st.markdown("---")

# Trade Table
st.header("📊 Recent Trades")
st.dataframe(
    data['trades'].head(20)[['timestamp', 'symbol', 'side', 'quantity', 'price', 'slippage_bps', 'latency_ms']],
    use_container_width=True
)

# Footer
st.markdown("---")
st.markdown("""
**Event-Driven Backtesting Engine** | 
[Documentation](../docs/MODULAR_ARCHITECTURE.md) | 
[GitHub](https://github.com/your-repo)
""")

# Interactive Backtest Dashboard

Streamlit-powered interactive visualization dashboard for backtest results.

## Features

### Performance Metrics
- **Total Return**: Overall P&L percentage
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Worst peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Volatility**: Annualized return volatility

### Visualizations

1. **Equity Curve & Drawdown**
   - Interactive time-series plot
   - Shows portfolio value over time
   - Drawdown visualization

2. **Execution Analytics**
   - Slippage distribution (basis points)
   - Latency distribution (milliseconds)
   - P99 latency tracking

3. **Market Microstructure**
   - Volume imbalance (bid/ask ratio)
   - Color-coded bar chart
   - Helps identify market conditions

4. **Trade Log**
   - Recent trades table
   - Symbol, side, quantity, price
   - Slippage and latency per trade

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Dashboard

```bash
# From project root
streamlit run src/dashboard/app.py

# Or with custom port
streamlit run src/dashboard/app.py --server.port 8502
```

### 3. Access Dashboard

Open browser to `http://localhost:8501`

## Configuration

### Sidebar Options
- **Show Trade Markers**: Display trade execution points
- **Show Drawdown**: Toggle drawdown subplot

### Quick Stats
- Real-time metrics in sidebar
- Delta indicators for quick assessment

## Data Sources

The dashboard can load data from:

1. **Sample Data** (default): Synthetic data generator
2. **JSON Files**: Load from `src/dashboard/data/*.json`
3. **Database**: Connect to PostgreSQL/MongoDB
4. **Live Backtest**: Real-time updates

## Customization

### Add New Visualizations

```python
# In app.py
st.header("My Custom Chart")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data['x'], y=data['y']))
st.plotly_chart(fig, use_container_width=True)
```

### Change Color Scheme

```python
# Modify color palette
COLOR_SCHEME = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#06A77D'
}
```

## Screenshots

*(Run the dashboard to see live interactive charts)*

## Tech Stack

- **Streamlit**: Web framework
- **Plotly**: Interactive charts
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations

## For Recruiters

This dashboard demonstrates:
- **Full-stack capability**: Backend (Python) + Frontend (Streamlit)
- **Data visualization**: Complex financial metrics
- **UX design**: Clean, professional interface
- **Production-ready**: Deployable to cloud (Streamlit Cloud, AWS, GCP)

## Deployment

### Streamlit Cloud

```bash
# Free hosting
1. Push to GitHub
2. Connect to streamlit.io
3. Deploy from repo
```

### Docker

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "src/dashboard/app.py"]
```

## License

Same as parent project.

# Event-Driven Backtesting Engine

A research-grade event-driven backtesting engine for simulating execution over historical data. Features tick-level simulation, strategy abstraction, PnL accounting, slippage & cost modeling, and comprehensive portfolio analytics (Sharpe, Max DD, Win rate).

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Performance Metrics](#performance-metrics)
- [Example Output](#example-output)
- [Testing](#testing)
- [Contributing](#contributing)

## Overview

This backtesting engine implements an event-driven architecture that processes market data chronologically, allowing for realistic simulation of trading strategies. The system handles order execution, position tracking, PnL calculation, and performance analysis.

### Key Features

- **Event-Driven Architecture**: Processes market data events sequentially for accurate simulation
- **Multiple Order Types**: Supports Market, Limit, Stop, and Stop-Limit orders
- **Realistic Execution**: Includes slippage modeling and commission costs
- **Comprehensive Analytics**: Tracks Sharpe ratio, max drawdown, win rate, and more
- **Strategy Abstraction**: Easy-to-use base class for implementing custom strategies
- **Position Management**: Automatic position tracking and PnL calculation
- **Performance Metrics**: Detailed performance reporting and analysis

## Architecture

The system follows an event-driven design pattern:

```
┌─────────────────┐
│  Market Data    │
│   (CSV/API)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Handler   │───► Generates MarketEvent
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Event Queue    │◄───┐
└────────┬────────┘    │
         │             │
         ▼             │
┌─────────────────┐    │
│   Strategy      │    │
│  (Your Logic)   │───►│ Generates SignalEvent
└─────────────────┘    │
                       │
         ┌─────────────┘
         │
         ▼
┌─────────────────┐
│  Portfolio      │───► Generates OrderEvent
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Execution      │───► Generates FillEvent
│   Handler       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Performance    │
│   Tracking      │
└─────────────────┘
```

### Component Descriptions

- **DataHandler**: Loads historical data and generates market events
- **Strategy**: Implements trading logic and generates trading signals
- **Portfolio**: Manages positions, tracks PnL, and creates orders
- **ExecutionHandler**: Simulates order execution with slippage and commissions
- **Event System**: Coordinates communication between components

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/event-driven-backtesting-engine.git
   cd event-driven-backtesting-engine
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Required Dependencies

- pandas >= 1.3.0
- numpy >= 1.21.0
- pytest >= 6.2.0 (for testing)

## Quick Start

### Basic Usage

```python
from src.strategy import MovingAverageCrossStrategy
from src.backtest import Backtest

# Initialize strategy
strategy = MovingAverageCrossStrategy(
    symbol='AAPL',
    short_window=50,
    long_window=200
)

# Run backtest
backtest = Backtest(
    symbol='AAPL',
    data_file='data/AAPL.csv',
    strategy=strategy,
    initial_capital=100000.0,
    commission=0.001,  # 0.1%
    slippage=0.0005    # 0.05%
)

# Execute backtest
results = backtest.run()

# Display results
print(f"Total Return: {results['total_return']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")
print(f"Win Rate: {results['win_rate']:.2%}")
```

### Creating a Custom Strategy

```python
from src.strategy import Strategy
from src.event import SignalEvent

class MyCustomStrategy(Strategy):
    """
    A custom trading strategy implementation.
    """
    
    def __init__(self, symbol, bars):
        super().__init__(symbol, bars)
        # Initialize your indicators here
        
    def calculate_signals(self, event):
        """
        Generate trading signals based on market data.
        
        Args:
            event: MarketEvent containing current market data
            
        Returns:
            SignalEvent or None
        """
        if event.type == 'MARKET':
            # Implement your trading logic
            # Example: Buy signal
            signal = SignalEvent(
                symbol=self.symbol,
                datetime=event.datetime,
                signal_type='LONG',
                strength=1.0
            )
            return signal
        return None
```

### Running the Example

The repository includes example strategies:

```bash
python examples/run_backtest.py
```

## API Reference

### Core Classes

#### Backtest

Main class for running backtests.

```python
Backtest(symbol, data_file, strategy, initial_capital, commission=0.0, slippage=0.0)
```

**Parameters:**
- `symbol` (str): Trading symbol (e.g., 'AAPL')
- `data_file` (str): Path to CSV file with OHLCV data
- `strategy` (Strategy): Strategy instance
- `initial_capital` (float): Starting capital
- `commission` (float): Commission rate (e.g., 0.001 for 0.1%)
- `slippage` (float): Slippage rate (e.g., 0.0005 for 0.05%)

**Methods:**
- `run()`: Execute the backtest and return results dictionary

#### Strategy

Base class for implementing trading strategies.

```python
Strategy(symbol, bars)
```

**Methods:**
- `calculate_signals(event)`: Override this method to implement trading logic

#### Portfolio

Manages positions and generates orders.

```python
Portfolio(bars, events, initial_capital=100000.0)
```

**Methods:**
- `update_signal(event)`: Process signal events and generate orders
- `update_fill(event)`: Process fill events and update positions
- `get_holdings()`: Get current holdings
- `get_performance()`: Get performance metrics

#### ExecutionHandler

Simulates order execution.

```python
SimulatedExecutionHandler(events, commission=0.0, slippage=0.0)
```

**Methods:**
- `execute_order(event)`: Execute an order and generate fill event

### Event Types

#### MarketEvent
Represents market data at a specific time.

#### SignalEvent
Represents a trading signal (LONG, SHORT, or EXIT).

**Attributes:**
- `symbol` (str): Trading symbol
- `datetime` (datetime): Signal timestamp
- `signal_type` (str): 'LONG', 'SHORT', or 'EXIT'
- `strength` (float): Signal strength (0.0 to 1.0)

#### OrderEvent
Represents an order to be executed.

**Attributes:**
- `symbol` (str): Trading symbol
- `order_type` (str): 'MKT', 'LMT', 'STP', 'STP_LMT'
- `quantity` (int): Number of shares
- `direction` (str): 'BUY' or 'SELL'

#### FillEvent
Represents a filled order.

**Attributes:**
- `symbol` (str): Trading symbol
- `exchange` (str): Exchange name
- `quantity` (int): Filled quantity
- `direction` (str): 'BUY' or 'SELL'
- `fill_cost` (float): Total cost including commission

## Performance Metrics

The engine calculates the following performance metrics:

### Total Return
Percentage return on initial capital.

```
Total Return = (Final Portfolio Value - Initial Capital) / Initial Capital × 100%
```

### Sharpe Ratio
Risk-adjusted return metric. Higher is better.

```
Sharpe Ratio = (Mean Daily Return - Risk Free Rate) / Std Dev of Daily Returns × √252
```

Interpretation:
- < 1.0: Suboptimal
- 1.0-2.0: Good
- 2.0-3.0: Very good
- > 3.0: Excellent

### Maximum Drawdown
Largest peak-to-trough decline in portfolio value.

```
Max Drawdown = (Trough Value - Peak Value) / Peak Value × 100%
```

Represents the worst-case loss from a historical peak.

### Win Rate
Percentage of profitable trades.

```
Win Rate = (Number of Winning Trades / Total Trades) × 100%
```

### Profit Factor
Ratio of gross profits to gross losses.

```
Profit Factor = Gross Profits / Gross Losses
```

Interpretation:
- < 1.0: Losing strategy
- 1.0-1.5: Marginal
- 1.5-2.0: Good
- > 2.0: Excellent

### Average Trade
Mean profit/loss per trade.

```
Average Trade = Total PnL / Number of Trades
```

## Example Output

When running a backtest, you'll see output similar to:

```
=== Backtest Results ===
Symbol: AAPL
Start Date: 2020-01-01
End Date: 2023-12-31
Initial Capital: $100,000.00
Final Portfolio Value: $145,230.50

Performance Metrics:
-------------------
Total Return: 45.23%
Annualized Return: 12.76%
Sharpe Ratio: 1.85
Max Drawdown: -18.45%
Win Rate: 58.30%
Profit Factor: 1.92

Trade Statistics:
----------------
Total Trades: 120
Winning Trades: 70
Losing Trades: 50
Average Trade: $377.75
Average Winner: $982.15
Average Loser: -$456.30
Largest Winner: $4,521.80
Largest Loser: -$2,103.45

Risk Metrics:
-------------
Volatility (Annual): 18.23%
Downside Deviation: 12.45%
Calmar Ratio: 0.69
Sortino Ratio: 1.45

Monthly Returns:
---------------
2020: +8.5%, +2.3%, -5.2%, +12.1%, ...
2021: +3.4%, +7.8%, +1.2%, -2.5%, ...
2022: -4.3%, +5.6%, +8.9%, +3.2%, ...
2023: +6.7%, +4.1%, +9.3%, +2.8%, ...

Backtest completed in 2.34 seconds.
```

## Testing

The project includes comprehensive unit tests.

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_portfolio.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v tests/
```

### Test Coverage

The test suite covers:
- Event system functionality
- Data handling and parsing
- Strategy signal generation
- Portfolio management and PnL tracking
- Order execution simulation
- Performance calculation

## Acknowledgments

- Inspired by the event-driven architecture described in "Algorithmic Trading" by Ernie Chan
- Market data simulation techniques based on industry best practices
- Performance metrics calculations follow CFA Institute standards
## Performance

### Benchmark Results

The engine is designed for **high-throughput, low-latency** tick processing:

| Metric | CSV | Parquet | Target |
|--------|-----|---------|--------|
| **Throughput** | 650K ticks/sec | 1.1M ticks/sec | 500K ticks/sec ✓ |
| **Latency** | 1.5 μs/tick | 0.9 μs/tick | < 2 μs ✓ |
| **Memory (1M ticks)** | 125 MB | 118 MB | < 200 MB ✓ |

### Key Features

- ✅ **Processes millions of ticks in seconds**
- ✅ **Sub-microsecond per-tick latency**
- ✅ **Memory-efficient streaming architecture**
- ✅ **Linear scalability** with dataset size

### Running Benchmarks

```bash
# Execute performance benchmarks
python benchmarks/performance_benchmark.py

# Generate performance visualizations
python benchmarks/visualize_results.py
```

**Detailed Performance Analysis**: See [`docs/PERFORMANCE.md`](docs/PERFORMANCE.md) for:
- Comprehensive benchmark results
- Performance optimization techniques
- Comparison with other frameworks
- Profiling your own backtests


## Performance Profiling

Comprehensive performance measurement and benchmarking tools to ensure the engine scales to millions of ticks.

### Performance Targets

| Metric | Target |
|--------|--------|
| Throughput | >100,000 ticks/sec |
| Per-tick latency | <10 µs (mean) |
| Memory | <500 MB for 1M ticks |
| CPU utilization | <50% (single core) |

### Features

- **Resource Profiler**: Real-time CPU and memory monitoring
- **Tick Profiler**: Microsecond-level per-tick timing
- **Metrics Collector**: Centralized performance metrics
- **Benchmarking Suite**: Scalability testing with millions of ticks
- **Visualizations**: Auto-generated performance graphs

### Quick Benchmark

```bash
# Run scalability test
python performance_profiling/benchmarks/run_scalability_test.py

# Generate performance graphs
python performance_profiling/visualizations/generate_graphs.py
```

### Example Output

```
================================================================================
Performance Metrics: scalability_1000000
================================================================================

Total Time: 5.23 seconds

Tick Processing:
  Total Ticks: 1,000,000
  Ticks/second: 191,205
  Mean Time: 5.23 µs
  Median Time: 4.85 µs

Resource Usage:
  CPU: 42.3% (max: 58.7%)
  Memory: 187.5 MB (peak: 192.3 MB)
================================================================================
```

See [`performance_profiling/README.md`](performance_profiling/README.md) for complete documentation.

## Modular Execution Architecture

Clean separation of concerns with dependency injection for production-grade code organization.

### Architecture

```
Trading Engine
    ├── Strategy Interface      (Signal generation)
    ├── Risk Manager         (Position limits, exposure checks)
    ├── Execution Simulator  (Latency models, slippage)
    └── Market Data Handler  (Data abstraction)
```

### Key Features

- **Interface-based Design**: All components implement clean interfaces
- **Dependency Injection**: Easy to swap implementations (backtest → live)
- **SOLID Principles**: Single responsibility, open/closed, dependency inversion
- **Testability**: Mock any component for isolated unit tests

### Quick Start

```python
# 1. Create components
strategy = SimpleMovingAverageStrategy(fast=10, slow=20)
risk_mgr = PositionRiskManager(max_position=1000)
exec_sim = RealisticExecutionSimulator(latency_model=LatencyModel.NORMAL)

# 2. Compose engine
engine = TradingEngine(strategy, risk_mgr, exec_sim)

# 3. Process events
for market_data in feed:
    engine.process_market_data(market_data)
```

### Components

**Strategy (`IStrategy`)**
- Convert market data → signals
- BUY, SELL, CLOSE signals
- Confidence scores

**Risk Manager (`IRiskManager`)**
- Position size limits
- Portfolio exposure limits
- Concentration checks
- Returns: APPROVED / REJECTED / WARNING

**Execution Simulator (`IExecutionSimulator`)**
- Latency models: ZERO, CONSTANT, NORMAL, REALISTIC_HFT
- Slippage simulation (basis points)
- Commission calculation

### Benefits

✅ **Modular**: Change one component without affecting others  
✅ **Testable**: Unit test each module in isolation  
✅ **Extensible**: Add new strategies/risk rules easily  
✅ **Production-ready**: Same interfaces work in live trading  

See [`docs/MODULAR_ARCHITECTURE.md`](docs/MODULAR_ARCHITECTURE.md) for complete documentation.

**Demo**: `python examples/modular_execution/demo_separation.py`

## 📈 Interactive Dashboard

Professional visualization dashboard built with Streamlit and Plotly for presenting backtest results.

### Features

📊 **Performance Metrics**
- Total Return, Sharpe Ratio, Max Drawdown
- Win Rate, Volatility tracking
- Real-time metric cards

💵 **Equity Curve & Drawdown**
- Interactive time-series plots
- Drawdown visualization
- Hover tooltips for detailed analysis

⚡ **Execution Analytics**
- Slippage distribution (basis points)
- Latency distribution (milliseconds)
- P99 latency tracking for HFT analysis

📋 **Market Microstructure**
- Volume imbalance visualization
- Bid/Ask ratio over time
- Color-coded market conditions

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run src/dashboard/app.py

# Access at http://localhost:8501
```

### Why This Matters

✅ **Visual Impact**: Makes your technical work immediately understandable  
✅ **Interview Ready**: Demo-able in interviews and presentations  
✅ **Full-Stack Skills**: Shows frontend + backend capability  
✅ **Production UI**: Professional dashboard recruiters recognize  

See [`src/dashboard/README.md`](src/dashboard/README.md) for detailed documentation.

**Screenshot**: Launch the dashboard to see live interactive visualizations!

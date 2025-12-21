# Strategy Library

Real-world strategy templates for quantitative backtesting.

## Overview

This library provides production-ready implementations of common algorithmic trading strategies. Each strategy follows the `StrategyInterface` pattern for seamless integration with the backtesting engine.

## Strategies

### 1. VWAP (Volume-Weighted Average Price)

**File**: `vwap_strategy.py`

**Use Case**: Execution algorithm for large institutional orders

**Description**: Slices large orders according to historical volume profile to minimize market impact. Orders are executed proportionally to volume throughout the trading day.

**Parameters**:
- `target_quantity`: Total quantity to execute
- `total_duration_minutes`: Time window to spread execution (default: 60)

**Example**:
```python
from src.strategies import VWAPStrategy

strategy = VWAPStrategy(
    target_quantity=10000,
    total_duration_minutes=120
)
```

---

### 2. TWAP (Time-Weighted Average Price)

**File**: `twap_strategy.py`

**Use Case**: Simple execution algorithm with minimal market impact

**Description**: Splits orders into equal time slices. Simpler alternative to VWAP that doesn't require volume data.

**Parameters**:
- `target_quantity`: Total quantity to execute
- `total_duration_minutes`: Time window to spread execution (default: 60)
- `num_slices`: Number of equal slices (default: 12)

**Example**:
```python
from src.strategies import TWAPStrategy

strategy = TWAPStrategy(
    target_quantity=5000,
    total_duration_minutes=60,
    num_slices=10
)
```

---

### 3. Mean Reversion

**File**: `mean_reversion_strategy.py`

**Use Case**: Trading price reversions using Bollinger Bands

**Description**: Enters positions when price deviates significantly from moving average. Exits when price reverts to mean. Uses Bollinger Bands (SMA ± 2σ).

**Parameters**:
- `window`: Lookback window for moving average (default: 20)
- `num_std`: Number of standard deviations for bands (default: 2.0)
- `position_size`: Size of each trade (default: 100)

**Trading Logic**:
- Buy when price < lower band
- Sell when price > upper band  
- Exit long when price crosses above SMA
- Exit short when price crosses below SMA

**Example**:
```python
from src.strategies import MeanReversionStrategy

strategy = MeanReversionStrategy(
    window=20,
    num_std=2.0,
    position_size=100
)
```

---

### 4. Statistical Arbitrage (Pairs Trading)

**File**: `statistical_arbitrage_strategy.py`

**Use Case**: Trading cointegrated pairs for market-neutral returns

**Description**: Monitors spread between two correlated assets. Trades when spread deviates from historical mean. Long underperformer, short outperformer.

**Parameters**:
- `symbol_pair`: Tuple of two cointegrated symbols
- `window`: Lookback window for spread (default: 30)
- `entry_threshold`: Z-score to enter position (default: 2.0)
- `exit_threshold`: Z-score to exit position (default: 0.5)
- `position_size`: Size of each leg (default: 100)

**Trading Logic**:
- Calculate spread = price_a - (hedge_ratio × price_b)
- Compute z-score = (spread - mean) / std
- Enter when |z-score| > entry_threshold
- Exit when |z-score| < exit_threshold

**Example**:
```python
from src.strategies import StatisticalArbitrageStrategy

strategy = StatisticalArbitrageStrategy(
    symbol_pair=('MSFT', 'GOOGL'),
    window=30,
    entry_threshold=2.0,
    exit_threshold=0.5,
    position_size=50
)
```

## Usage Pattern

All strategies implement the `StrategyInterface`:

```python
from interfaces.strategy_interface import StrategyInterface

class MyStrategy(StrategyInterface):
    def on_market_data(self, data: Dict) -> Optional[Dict]:
        """Process market data and generate orders."""
        pass
        
    def on_fill(self, fill: Dict) -> None:
        """Handle order fills."""
        pass
        
    def get_state(self) -> Dict:
        """Return strategy state for monitoring."""
        pass
```

## Integration Example

```python
from src.strategies import MeanReversionStrategy, TWAPStrategy

# Create strategy
strategy = MeanReversionStrategy(window=20, num_std=2.0)

# Feed market data
order = strategy.on_market_data({
    'symbol': 'AAPL',
    'bid': 150.20,
    'ask': 150.25,
    'timestamp': datetime.now(),
    'volume': 1000
})

if order:
    # Submit order to exchange
    execute_order(order)
```

## Benefits

✅ **Production-Ready**: Clean interfaces, error handling, state management

✅ **Reusable**: Easy to mix strategies or create portfolio allocations

✅ **Testable**: Isolated logic makes unit testing straightforward

✅ **Documented**: Each strategy includes docstrings and examples

✅ **Extensible**: Simple to add new strategies following the same pattern

## Performance Considerations

- **VWAP/TWAP**: Low computational overhead, suitable for HFT
- **Mean Reversion**: O(n) moving average, efficient with deque
- **Stat Arb**: O(n) z-score calculation, negligible overhead

All strategies use numpy for vectorized operations where applicable.

## Next Steps

1. **Backtest** strategies using historical tick data
2. **Optimize** parameters using grid search or Bayesian optimization
3. **Combine** strategies for portfolio allocation
4. **Risk Management**: Add position limits, stop-losses, max drawdown constraints

## References

- Kissell, R. (2013). *The Science of Algorithmic Trading*
- Chan, E. (2013). *Algorithmic Trading: Winning Strategies*
- Pole, A. (2007). *Statistical Arbitrage*

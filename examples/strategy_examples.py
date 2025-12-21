"""
Strategy Library Usage Examples

Demonstrates how to use the real-world strategy templates.
"""

from datetime import datetime
from src.strategies import (
    VWAPStrategy,
    TWAPStrategy,
    MeanReversionStrategy,
    StatisticalArbitrageStrategy
)


def demo_vwap_strategy():
    """Demonstrate VWAP execution strategy."""
    print("\n" + "="*60)
    print("VWAP Strategy Example")
    print("="*60)
    
    # Create strategy to execute 10,000 shares over 2 hours
    strategy = VWAPStrategy(
        target_quantity=10000,
        total_duration_minutes=120
    )
    
    # Simulate market data
    market_data = {
        'symbol': 'AAPL',
        'bid': 175.20,
        'ask': 175.25,
        'volume': 5000,
        'timestamp': datetime(2024, 1, 15, 10, 0, 0)
    }
    
    order = strategy.on_market_data(market_data)
    
    if order:
        print(f"\nGenerated Order:")
        print(f"  Symbol: {order['symbol']}")
        print(f"  Side: {order['side']}")
        print(f"  Quantity: {order['quantity']}")
        print(f"  Price: ${order['price']:.2f}")
        print(f"  Type: {order['order_type']}")
    
    state = strategy.get_state()
    print(f"\nStrategy State:")
    print(f"  Executed: {state['executed']} / {state['target']}")
    print(f"  Completion: {state['completion']:.1%}")


def demo_twap_strategy():
    """Demonstrate TWAP execution strategy."""
    print("\n" + "="*60)
    print("TWAP Strategy Example")
    print("="*60)
    
    # Split 5,000 shares into 10 equal slices over 1 hour
    strategy = TWAPStrategy(
        target_quantity=5000,
        total_duration_minutes=60,
        num_slices=10
    )
    
    market_data = {
        'symbol': 'MSFT',
        'bid': 380.15,
        'ask': 380.20,
        'timestamp': datetime(2024, 1, 15, 10, 0, 0)
    }
    
    order = strategy.on_market_data(market_data)
    
    if order:
        print(f"\nGenerated Order (First Slice):")
        print(f"  Symbol: {order['symbol']}")
        print(f"  Side: {order['side']}")
        print(f"  Quantity: {order['quantity']}")
        print(f"  Price: ${order['price']:.2f}")
    
    state = strategy.get_state()
    print(f"\nStrategy State:")
    print(f"  Slices Completed: {state['slices_completed']} / {state['total_slices']}")
    print(f"  Executed: {state['executed']} / {state['target']}")
    print(f"  Completion: {state['completion']:.1%}")


def demo_mean_reversion():
    """Demonstrate Mean Reversion strategy."""
    print("\n" + "="*60)
    print("Mean Reversion Strategy Example")
    print("="*60)
    
    strategy = MeanReversionStrategy(
        window=20,
        num_std=2.0,
        position_size=100
    )
    
    # Simulate price series
    print("\nFeeding price data...")
    prices = [150.0 + i * 0.5 for i in range(15)]  # Trending up
    prices.extend([155.0 - i * 0.3 for i in range(10)])  # Drop below mean
    
    order = None
    for i, price in enumerate(prices):
        market_data = {
            'symbol': 'GOOGL',
            'bid': price - 0.05,
            'ask': price + 0.05,
            'timestamp': datetime(2024, 1, 15, 10, i, 0)
        }
        
        new_order = strategy.on_market_data(market_data)
        if new_order:
            order = new_order
            print(f"\n[Bar {i}] Signal Generated!")
    
    if order:
        print(f"\nGenerated Order:")
        print(f"  Symbol: {order['symbol']}")
        print(f"  Side: {order['side']}")
        print(f"  Quantity: {order['quantity']}")
        print(f"  Price: ${order['price']:.2f}")
        print(f"  Strategy: {order['strategy']}")
    
    state = strategy.get_state()
    if state['sma']:
        print(f"\nStrategy State:")
        print(f"  Position: {state['position']}")
        print(f"  SMA: ${state['sma']:.2f}")
        print(f"  Std Dev: ${state['std']:.2f}")
        print(f"  Entry Price: ${state['entry_price']:.2f}" if state['entry_price'] else "  No position")


def demo_statistical_arbitrage():
    """Demonstrate Statistical Arbitrage (Pairs Trading) strategy."""
    print("\n" + "="*60)
    print("Statistical Arbitrage Strategy Example")
    print("="*60)
    
    strategy = StatisticalArbitrageStrategy(
        symbol_pair=('MSFT', 'GOOGL'),
        window=30,
        entry_threshold=2.0,
        exit_threshold=0.5,
        position_size=50
    )
    
    print("\nMonitoring MSFT-GOOGL spread...")
    
    # Simulate correlated price movements
    for i in range(35):
        # MSFT price
        msft_price = 380.0 + i * 0.2
        market_data_a = {
            'symbol': 'MSFT',
            'bid': msft_price - 0.05,
            'ask': msft_price + 0.05,
            'timestamp': datetime(2024, 1, 15, 10, i, 0)
        }
        
        order_a = strategy.on_market_data(market_data_a)
        
        # GOOGL price (diverging)
        googl_price = 150.0 + i * 0.05  # Moving slower
        market_data_b = {
            'symbol': 'GOOGL',
            'bid': googl_price - 0.05,
            'ask': googl_price + 0.05,
            'timestamp': datetime(2024, 1, 15, 10, i, 0)
        }
        
        order_b = strategy.on_market_data(market_data_b)
        
        if order_a or order_b:
            print(f"\n[Bar {i}] Trade Signal!")
            if order_a:
                print(f"  {order_a['symbol']}: {order_a['side']} {order_a['quantity']} @ ${order_a['price']:.2f}")
            if order_b:
                print(f"  {order_b['symbol']}: {order_b['side']} {order_b['quantity']} @ ${order_b['price']:.2f}")
    
    state = strategy.get_state()
    if state['z_score'] is not None:
        print(f"\nStrategy State:")
        print(f"  Position MSFT: {state['position_a']}")
        print(f"  Position GOOGL: {state['position_b']}")
        print(f"  Z-Score: {state['z_score']:.2f}")
        print(f"  Hedge Ratio: {state['hedge_ratio']:.2f}")


if __name__ == '__main__':
    print("\n" + "#"*60)
    print("# Strategy Library Examples")
    print("#"*60)
    
    demo_vwap_strategy()
    demo_twap_strategy()
    demo_mean_reversion()
    demo_statistical_arbitrage()
    
    print("\n" + "#"*60)
    print("# Examples Complete!")
    print("#"*60 + "\n")

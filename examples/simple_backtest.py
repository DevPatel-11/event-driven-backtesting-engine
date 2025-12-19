#!/usr/bin/env python3
"""Simple backtest example using the event-driven backtesting engine."""

import sys
import os
from datetime import datetime

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.backtest_engine import BacktestEngine
from src.market_data.data_handler import CSVDataHandler
from src.strategy.base_strategy import BuyAndHoldStrategy
from src.portfolio.portfolio import Portfolio
from src.execution.execution import ExecutionHandler


def run_backtest():
    """Run a simple backtest with BuyAndHoldStrategy."""
    
    # Configuration
    csv_dir = os.path.join(os.path.dirname(__file__), 'data')
    symbol_list = ['AAPL']
    initial_capital = 100000.0
    start_date = datetime(2023, 1, 1)
    
    print("="*60)
    print("Event-Driven Backtesting Engine - Simple Example")
    print("="*60)
    print(f"\nBacktest Configuration:")
    print(f"  Strategy: Buy and Hold")
    print(f"  Symbols: {', '.join(symbol_list)}")
    print(f"  Initial Capital: ${initial_capital:,.2f}")
    print(f"  Data Directory: {csv_dir}")
    print(f"  Start Date: {start_date.strftime('%Y-%m-%d')}")
    print("\nRunning backtest...")
    
    # Initialize backtest engine
    engine = BacktestEngine(
        csv_dir=csv_dir,
        symbol_list=symbol_list,
        initial_capital=initial_capital,
        start_date=start_date,
        data_handler_cls=CSVDataHandler,
        execution_handler_cls=ExecutionHandler,
        portfolio_cls=Portfolio,
        strategy_cls=BuyAndHoldStrategy
    )
    
    # Run backtest
    metrics, equity_curve = engine.run()
    
    # Display results
    print("\n" + "="*60)
    print("Backtest Results")
    print("="*60)
    
    print(f"\nPerformance Metrics:")
    print(f"  Total Return: {metrics['total_return']*100:.2f}%")
    print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
    print(f"  Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
    print(f"  Win Rate: {metrics['win_rate']*100:.2f}%")
    print(f"  Final Equity: ${metrics['final_equity']:,.2f}")
    
    print(f"\nExecution Statistics:")
    print(f"  Total Signals: {metrics['signals']}")
    print(f"  Total Orders: {metrics['orders']}")
    print(f"  Total Fills: {metrics['fills']}")
    print(f"  Total Trades: {metrics['total_trades']}")
    
    print("\n" + "="*60)
    print("Backtest completed successfully!")
    print("="*60)
    
    return metrics, equity_curve


if __name__ == '__main__':
    try:
        metrics, equity_curve = run_backtest()
    except Exception as e:
        print(f"\nError running backtest: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

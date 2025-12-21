#!/usr/bin/env python3
"""Demonstration of clean modular architecture with dependency injection."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.interfaces.strategy_interface import IStrategy, Signal, SignalType
from src.interfaces.risk_interface import IRiskManager, RiskStatus
from src.interfaces.execution_interface import IExecutionSimulator, LatencyModel
from src.risk.position_risk_manager import PositionRiskManager
from src.execution_sim.realistic_execution_simulator import RealisticExecutionSimulator
from typing import Dict, Any, Optional


# Example Strategy Implementation
class SimpleMovingAverageStrategy(IStrategy):
    """Example strategy: Simple moving average crossover."""
    
    def __init__(self, fast_period: int = 10, slow_period: int = 20):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.price_history = []
    
    def on_market_data(self, market_data: Dict[str, Any]) -> Optional[Signal]:
        price = market_data.get('price', 0.0)
        self.price_history.append(price)
        
        if len(self.price_history) < self.slow_period:
            return None
        
        fast_ma = sum(self.price_history[-self.fast_period:]) / self.fast_period
        slow_ma = sum(self.price_history[-self.slow_period:]) / self.slow_period
        
        if fast_ma > slow_ma:
            return Signal(
                symbol=market_data['symbol'],
                signal_type=SignalType.BUY,
                quantity=100.0,
                timestamp=market_data['timestamp'],
                price=price,
                confidence=0.7
            )
        return None
    
    def on_fill(self, fill_event: Dict[str, Any]) -> None:
        print(f"  [{self.name}] Fill received: {fill_event}")
    
    def reset(self) -> None:
        self.price_history = []
    
    @property
    def name(self) -> str:
        return f"SMA_{self.fast_period}_{self.slow_period}"


class TradingEngine:
    """Trading engine with clean dependency injection."""
    
    def __init__(self,
                 strategy: IStrategy,
                 risk_manager: IRiskManager,
                 execution_simulator: IExecutionSimulator):
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.execution_simulator = execution_simulator
        self.positions = {}
    
    def process_market_data(self, market_data: Dict[str, Any]):
        # 1. Strategy generates signal
        signal = self.strategy.on_market_data(market_data)
        if not signal:
            return
        
        print(f"\nSignal generated: {signal.signal_type.value} {signal.quantity} @ {signal.price}")
        
        # 2. Risk manager checks order
        risk_result = self.risk_manager.check_order(signal, self.positions)
        print(f"Risk check: {risk_result.status.value} - {risk_result.reason}")
        
        if risk_result.status == RiskStatus.REJECTED:
            return
        
        # 3. Execution simulator executes order
        exec_result = self.execution_simulator.execute_order(
            signal,
            market_data['price'],
            market_data['timestamp']
        )
        print(f"Execution: Filled {exec_result.filled_quantity} @ {exec_result.filled_price:.2f}")
        print(f"           Latency: {exec_result.latency_ms:.2f}ms, Slippage: ${exec_result.slippage:.4f}")
        
        # Update positions
        self.positions[signal.symbol] = self.positions.get(signal.symbol, 0) + signal.quantity
        
        # Notify strategy of fill
        self.strategy.on_fill({'order_id': exec_result.order_id, 'filled_quantity': exec_result.filled_quantity})


def main():
    print("=" * 80)
    print("Modular Architecture Demonstration")
    print("=" * 80)
    
    # 1. Configure each component independently
    strategy = SimpleMovingAverageStrategy(fast_period=5, slow_period=10)
    
    risk_manager = PositionRiskManager(
        max_position_size=500.0,
        max_portfolio_exposure=50000.0,
        max_concentration=0.3
    )
    
    execution_sim = RealisticExecutionSimulator(
        latency_model=LatencyModel.NORMAL,
        latency_params={'mean_ms': 3.0, 'std_ms': 1.0},
        slippage_bps=1.5
    )
    
    # 2. Inject dependencies into engine
    engine = TradingEngine(strategy, risk_manager, execution_sim)
    
    # 3. Simulate market data
    import time
    prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
    
    print("\nProcessing market data...")
    for i, price in enumerate(prices):
        market_data = {
            'symbol': 'AAPL',
            'price': price,
            'timestamp': time.time() + i,
            'volume': 1000
        }
        engine.process_market_data(market_data)
    
    print("\n" + "=" * 80)
    print(f"Final Positions: {engine.positions}")
    print("=" * 80)

if __name__ == '__main__':
    main()

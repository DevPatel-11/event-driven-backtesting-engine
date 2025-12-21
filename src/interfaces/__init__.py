"""Clean interfaces for modular execution model."""

from .strategy_interface import IStrategy, Signal, SignalType
from .risk_interface import IRiskManager, RiskCheckResult
from .execution_interface import IExecutionSimulator, ExecutionResult, LatencyModel
from .market_data_interface import IMarketDataHandler, MarketDataSnapshot

__all__ = [
    'IStrategy', 'Signal', 'SignalType',
    'IRiskManager', 'RiskCheckResult',
    'IExecutionSimulator', 'ExecutionResult', 'LatencyModel',
    'IMarketDataHandler', 'MarketDataSnapshot'
]

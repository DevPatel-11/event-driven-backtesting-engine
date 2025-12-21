"""
Strategy Library

Collection of real-world trading strategies for backtesting.
"""

from .vwap_strategy import VWAPStrategy
from .twap_strategy import TWAPStrategy
from .mean_reversion_strategy import MeanReversionStrategy
from .statistical_arbitrage_strategy import StatisticalArbitrageStrategy

__all__ = [
    'VWAPStrategy',
    'TWAPStrategy',
    'MeanReversionStrategy',
    'StatisticalArbitrageStrategy'
]

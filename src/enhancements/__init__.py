"""Enhancements module for advanced backtesting features."""
from .asset_classes import AssetClass, MultiAssetPortfolio
from .slippage_models import SlippageModel, FixedSlippage, VolumeBasedSlippage, SquareRootSlippage
from .latency import LatencyModel, FixedLatency, VariableLatency
from .parallel_backtest import ParallelBacktestRunner
from .visualization import EquityCurveVisualizer, PerformanceVisualizer

__all__ = [
    'AssetClass',
    'MultiAssetPortfolio',
    'SlippageModel',
    'FixedSlippage',
    'VolumeBasedSlippage',
    'SquareRootSlippage',
    'LatencyModel',
    'FixedLatency',
    'VariableLatency',
    'ParallelBacktestRunner',
    'EquityCurveVisualizer',
    'PerformanceVisualizer',
]

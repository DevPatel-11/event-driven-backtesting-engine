import pytest
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.performance import PerformanceMetrics


def test_sharpe_ratio_positive():
    """Test Sharpe ratio calculation with positive returns."""
    returns = pd.Series([0.01, 0.02, 0.01, 0.03, 0.02])
    sharpe = PerformanceMetrics.calculate_sharpe_ratio(returns, periods=252)
    assert sharpe > 0
    assert isinstance(sharpe, float)


def test_sharpe_ratio_zero_std():
    """Test Sharpe ratio with zero standard deviation."""
    returns = pd.Series([0.01, 0.01, 0.01, 0.01, 0.01])
    sharpe = PerformanceMetrics.calculate_sharpe_ratio(returns)
    assert sharpe == 0.0


def test_sharpe_ratio_insufficient_data():
    """Test Sharpe ratio with insufficient data."""
    returns = pd.Series([0.01])
    sharpe = PerformanceMetrics.calculate_sharpe_ratio(returns)
    assert sharpe == 0.0


def test_max_drawdown():
    """Test maximum drawdown calculation."""
    equity = pd.Series([100000, 105000, 103000, 107000, 104000])
    max_dd = PerformanceMetrics.calculate_max_drawdown(equity)
    assert max_dd < 0  # Drawdown should be negative
    assert isinstance(max_dd, float)


def test_max_drawdown_no_drawdown():
    """Test maximum drawdown with no drawdown (always increasing)."""
    equity = pd.Series([100000, 105000, 110000, 115000])
    max_dd = PerformanceMetrics.calculate_max_drawdown(equity)
    assert max_dd == 0.0


def test_max_drawdown_empty():
    """Test maximum drawdown with empty series."""
    equity = pd.Series([])
    max_dd = PerformanceMetrics.calculate_max_drawdown(equity)
    assert max_dd == 0.0


def test_win_rate():
    """Test win rate calculation."""
    returns = pd.Series([0.01, -0.02, 0.03, 0.01, -0.01])
    win_rate = PerformanceMetrics.calculate_win_rate(returns)
    assert 0.0 <= win_rate <= 1.0
    assert win_rate == 0.6  # 3 out of 5 are positive


def test_win_rate_all_positive():
    """Test win rate with all positive returns."""
    returns = pd.Series([0.01, 0.02, 0.03])
    win_rate = PerformanceMetrics.calculate_win_rate(returns)
    assert win_rate == 1.0


def test_win_rate_all_negative():
    """Test win rate with all negative returns."""
    returns = pd.Series([-0.01, -0.02, -0.03])
    win_rate = PerformanceMetrics.calculate_win_rate(returns)
    assert win_rate == 0.0


def test_win_rate_empty():
    """Test win rate with empty returns."""
    returns = pd.Series([])
    win_rate = PerformanceMetrics.calculate_win_rate(returns)
    assert win_rate == 0.0


def test_calculate_metrics_complete():
    """Test complete metrics calculation."""
    equity_curve = pd.DataFrame({
        'total': [100000, 105000, 103000, 107000, 104000, 108000],
        'datetime': pd.date_range('2023-01-01', periods=6, freq='D')
    })
    
    metrics = PerformanceMetrics.calculate_metrics(equity_curve)
    
    assert 'total_return' in metrics
    assert 'sharpe_ratio' in metrics
    assert 'max_drawdown' in metrics
    assert 'win_rate' in metrics
    assert 'total_trades' in metrics
    assert 'final_equity' in metrics
    
    assert metrics['final_equity'] == 108000
    assert metrics['total_return'] > 0
    assert metrics['total_trades'] == 5


def test_calculate_metrics_empty():
    """Test metrics calculation with empty DataFrame."""
    equity_curve = pd.DataFrame()
    metrics = PerformanceMetrics.calculate_metrics(equity_curve)
    
    assert metrics['total_return'] == 0.0
    assert metrics['sharpe_ratio'] == 0.0
    assert metrics['max_drawdown'] == 0.0
    assert metrics['win_rate'] == 0.0
    assert metrics['total_trades'] == 0
    assert metrics['final_equity'] == 0.0


def test_calculate_metrics_no_total_column():
    """Test metrics calculation without 'total' column."""
    equity_curve = pd.DataFrame({
        'cash': [100000, 105000, 103000],
        'datetime': pd.date_range('2023-01-01', periods=3, freq='D')
    })
    
    metrics = PerformanceMetrics.calculate_metrics(equity_curve)
    
    assert metrics['total_return'] == 0.0
    assert metrics['final_equity'] == 0.0

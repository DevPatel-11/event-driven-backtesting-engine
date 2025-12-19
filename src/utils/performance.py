import pandas as pd
import numpy as np
from typing import Dict


class PerformanceMetrics:
    """Calculate portfolio performance metrics."""
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, periods: int = 252) -> float:
        """Calculate annualized Sharpe ratio.
        
        Args:
            returns: Series of returns
            periods: Number of periods per year (252 for daily, 12 for monthly)
        
        Returns:
            Annualized Sharpe ratio
        """
        if len(returns) < 2 or returns.std() == 0:
            return 0.0
        return np.sqrt(periods) * (returns.mean() / returns.std())
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown percentage.
        
        Args:
            equity_curve: Series of equity values
        
        Returns:
            Maximum drawdown as negative percentage
        """
        if len(equity_curve) == 0:
            return 0.0
        
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        return drawdown.min()
    
    @staticmethod
    def calculate_win_rate(returns: pd.Series) -> float:
        """Calculate win rate (percentage of profitable periods).
        
        Args:
            returns: Series of returns
        
        Returns:
            Win rate as decimal (0.0 to 1.0)
        """
        if len(returns) == 0:
            return 0.0
        winning_trades = (returns > 0).sum()
        return winning_trades / len(returns)
    
    @staticmethod
    def calculate_metrics(equity_curve: pd.DataFrame) -> Dict[str, float]:
        """Calculate all performance metrics from equity curve.
        
        Args:
            equity_curve: DataFrame with 'total' column containing equity values
        
        Returns:
            Dictionary with performance metrics
        """
        if len(equity_curve) == 0 or 'total' not in equity_curve.columns:
            return {
                'total_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'total_trades': 0,
                'final_equity': 0.0
            }
        
        equity = equity_curve['total']
        returns = equity.pct_change().dropna()
        
        metrics = {
            'total_return': (equity.iloc[-1] / equity.iloc[0] - 1) if len(equity) > 0 else 0.0,
            'sharpe_ratio': PerformanceMetrics.calculate_sharpe_ratio(returns),
            'max_drawdown': PerformanceMetrics.calculate_max_drawdown(equity),
            'win_rate': PerformanceMetrics.calculate_win_rate(returns),
            'total_trades': len(returns),
            'final_equity': equity.iloc[-1] if len(equity) > 0 else 0.0
        }
        
        return metrics

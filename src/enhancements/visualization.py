"""Visualization utilities for backtest results."""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    warnings.warn("Matplotlib not available. Install with: pip install matplotlib")


class EquityCurveVisualizer:
    """
    Visualizer for equity curves and portfolio performance.
    
    Creates professional-looking charts for analyzing backtest results.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize equity curve visualizer.
        
        Args:
            figsize: Figure size (width, height) in inches
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib is required for visualization")
        
        self.figsize = figsize
        self.fig = None
        self.axes = None
    
    def plot_equity_curve(self, equity_data: pd.Series, 
                         title: str = "Portfolio Equity Curve",
                         show_drawdown: bool = True) -> Figure:
        """
        Plot equity curve with optional drawdown overlay.
        
        Args:
            equity_data: Series of portfolio values indexed by datetime
            title: Chart title
            show_drawdown: Whether to show drawdown in subplot
            
        Returns:
            Matplotlib figure
        """
        if show_drawdown:
            self.fig, self.axes = plt.subplots(2, 1, figsize=self.figsize,
                                              gridspec_kw={'height_ratios': [3, 1]})
            ax_equity, ax_dd = self.axes
        else:
            self.fig, ax_equity = plt.subplots(figsize=self.figsize)
        
        # Plot equity curve
        ax_equity.plot(equity_data.index, equity_data.values, 
                      linewidth=2, color='#2E86AB', label='Portfolio Value')
        ax_equity.fill_between(equity_data.index, equity_data.values, 
                              alpha=0.3, color='#2E86AB')
        
        # Add horizontal line at initial value
        initial_value = equity_data.iloc[0]
        ax_equity.axhline(y=initial_value, color='gray', linestyle='--', 
                         alpha=0.5, label=f'Initial: ${initial_value:,.0f}')
        
        ax_equity.set_title(title, fontsize=14, fontweight='bold')
        ax_equity.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax_equity.legend(loc='upper left')
        ax_equity.grid(True, alpha=0.3)
        ax_equity.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        
        # Plot drawdown if requested
        if show_drawdown:
            running_max = equity_data.cummax()
            drawdown = (equity_data - running_max) / running_max * 100
            
            ax_dd.fill_between(drawdown.index, drawdown.values, 0,
                              color='#A23B72', alpha=0.5)
            ax_dd.set_ylabel('Drawdown (%)', fontsize=12)
            ax_dd.set_xlabel('Date', fontsize=12)
            ax_dd.grid(True, alpha=0.3)
            ax_dd.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        
        plt.tight_layout()
        return self.fig
    
    def plot_comparison(self, equity_curves: Dict[str, pd.Series],
                       title: str = "Strategy Comparison") -> Figure:
        """
        Compare multiple equity curves.
        
        Args:
            equity_curves: Dictionary of {strategy_name: equity_series}
            title: Chart title
            
        Returns:
            Matplotlib figure
        """
        self.fig, ax = plt.subplots(figsize=self.figsize)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(equity_curves)))
        
        for (name, equity), color in zip(equity_curves.items(), colors):
            # Normalize to percentage returns
            normalized = (equity / equity.iloc[0] - 1) * 100
            ax.plot(normalized.index, normalized.values, 
                   label=name, linewidth=2, color=color)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Return (%)', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        
        plt.tight_layout()
        return self.fig
    
    def save(self, filename: str, dpi: int = 300):
        """
        Save figure to file.
        
        Args:
            filename: Output filename
            dpi: Resolution in dots per inch
        """
        if self.fig is not None:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    
    def show(self):
        """Display the figure."""
        if self.fig is not None:
            plt.show()


class PerformanceVisualizer:
    """
    Visualizer for performance metrics and statistics.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize performance visualizer.
        
        Args:
            figsize: Figure size (width, height) in inches
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib is required for visualization")
        
        self.figsize = figsize
        self.fig = None
    
    def plot_returns_distribution(self, returns: pd.Series,
                                 title: str = "Returns Distribution") -> Figure:
        """
        Plot distribution of returns.
        
        Args:
            returns: Series of returns
            title: Chart title
            
        Returns:
            Matplotlib figure
        """
        self.fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)
        
        # Histogram
        ax1.hist(returns.dropna(), bins=50, color='#2E86AB', 
                alpha=0.7, edgecolor='black')
        ax1.axvline(returns.mean(), color='red', linestyle='--',
                   label=f'Mean: {returns.mean()*100:.2f}%')
        ax1.set_xlabel('Return (%)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('Histogram', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Q-Q plot
        from scipy import stats
        stats.probplot(returns.dropna(), dist="norm", plot=ax2)
        ax2.set_title('Q-Q Plot', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        self.fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return self.fig
    
    def plot_rolling_metrics(self, equity_data: pd.Series,
                            window: int = 252,
                            title: str = "Rolling Performance Metrics") -> Figure:
        """
        Plot rolling Sharpe ratio and volatility.
        
        Args:
            equity_data: Series of portfolio values
            window: Rolling window size (default: 252 days)
            title: Chart title
            
        Returns:
            Matplotlib figure
        """
        # Calculate returns
        returns = equity_data.pct_change()
        
        # Rolling Sharpe (annualized)
        rolling_sharpe = (returns.rolling(window).mean() / 
                         returns.rolling(window).std() * np.sqrt(252))
        
        # Rolling volatility (annualized)
        rolling_vol = returns.rolling(window).std() * np.sqrt(252) * 100
        
        self.fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize)
        
        # Sharpe ratio
        ax1.plot(rolling_sharpe.index, rolling_sharpe.values,
                color='#2E86AB', linewidth=2)
        ax1.axhline(y=1.0, color='green', linestyle='--', alpha=0.5, label='Sharpe=1')
        ax1.set_ylabel('Sharpe Ratio', fontsize=12)
        ax1.set_title(f'{window}-Day Rolling Sharpe Ratio', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Volatility
        ax2.plot(rolling_vol.index, rolling_vol.values,
                color='#A23B72', linewidth=2)
        ax2.set_ylabel('Volatility (%)', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_title(f'{window}-Day Rolling Volatility', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        self.fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return self.fig
    
    def plot_monthly_returns_heatmap(self, returns: pd.Series,
                                    title: str = "Monthly Returns Heatmap") -> Figure:
        """
        Plot heatmap of monthly returns.
        
        Args:
            returns: Series of returns indexed by datetime
            title: Chart title
            
        Returns:
            Matplotlib figure
        """
        # Resample to monthly returns
        monthly_returns = (1 + returns).resample('M').prod() - 1
        
        # Create pivot table
        monthly_returns_pivot = monthly_returns.to_frame('returns')
        monthly_returns_pivot['Year'] = monthly_returns_pivot.index.year
        monthly_returns_pivot['Month'] = monthly_returns_pivot.index.month
        pivot = monthly_returns_pivot.pivot(index='Year', columns='Month', values='returns')
        pivot = pivot * 100  # Convert to percentage
        
        # Plot heatmap
        self.fig, ax = plt.subplots(figsize=self.figsize)
        im = ax.imshow(pivot.values, cmap='RdYlGn', aspect='auto',
                      vmin=-pivot.abs().max().max(), vmax=pivot.abs().max().max())
        
        # Set ticks
        ax.set_xticks(np.arange(12))
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        ax.set_yticklabels(pivot.index)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Return (%)', fontsize=12)
        
        # Add text annotations
        for i in range(len(pivot.index)):
            for j in range(12):
                if not np.isnan(pivot.iloc[i, j]):
                    text = ax.text(j, i, f'{pivot.iloc[i, j]:.1f}',
                                 ha="center", va="center", color="black",
                                 fontsize=8)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return self.fig
    
    def save(self, filename: str, dpi: int = 300):
        """Save figure to file."""
        if self.fig is not None:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    
    def show(self):
        """Display the figure."""
        if self.fig is not None:
            plt.show()

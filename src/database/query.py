"""Query utilities for advanced database operations."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import Session
from .models import BacktestRun, Trade, PerformanceMetric


class BacktestQueryBuilder:
    """Advanced query builder for backtest data."""
    
    def __init__(self, session: Session):
        """Initialize query builder.
        
        Args:
            session: Database session
        """
        self.session = session
        self._filters = []
        self._order_by = None
        self._limit = None
    
    def filter_by_strategy(self, strategy_name: str) -> 'BacktestQueryBuilder':
        """Filter by strategy name.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            Self for chaining
        """
        self._filters.append(BacktestRun.strategy_name == strategy_name)
        return self
    
    def filter_by_symbol(self, symbol: str) -> 'BacktestQueryBuilder':
        """Filter by trading symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Self for chaining
        """
        self._filters.append(BacktestRun.symbol == symbol)
        return self
    
    def filter_by_date_range(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> 'BacktestQueryBuilder':
        """Filter by date range.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Self for chaining
        """
        if start_date:
            self._filters.append(BacktestRun.start_date >= start_date)
        if end_date:
            self._filters.append(BacktestRun.end_date <= end_date)
        return self
    
    def filter_by_sharpe_ratio(
        self,
        min_sharpe: Optional[float] = None,
        max_sharpe: Optional[float] = None
    ) -> 'BacktestQueryBuilder':
        """Filter by Sharpe ratio range.
        
        Args:
            min_sharpe: Minimum Sharpe ratio
            max_sharpe: Maximum Sharpe ratio
            
        Returns:
            Self for chaining
        """
        if min_sharpe is not None:
            self._filters.append(BacktestRun.sharpe_ratio >= min_sharpe)
        if max_sharpe is not None:
            self._filters.append(BacktestRun.sharpe_ratio <= max_sharpe)
        return self
    
    def order_by_created(self, ascending: bool = False) -> 'BacktestQueryBuilder':
        """Order results by creation date.
        
        Args:
            ascending: Sort ascending if True, descending if False
            
        Returns:
            Self for chaining
        """
        self._order_by = asc(BacktestRun.created_at) if ascending else desc(BacktestRun.created_at)
        return self
    
    def order_by_return(self, ascending: bool = False) -> 'BacktestQueryBuilder':
        """Order results by total return.
        
        Args:
            ascending: Sort ascending if True, descending if False
            
        Returns:
            Self for chaining
        """
        self._order_by = asc(BacktestRun.total_return) if ascending else desc(BacktestRun.total_return)
        return self
    
    def limit(self, count: int) -> 'BacktestQueryBuilder':
        """Limit number of results.
        
        Args:
            count: Maximum number of results
            
        Returns:
            Self for chaining
        """
        self._limit = count
        return self
    
    def execute(self) -> List[BacktestRun]:
        """Execute the query and return results.
        
        Returns:
            List of matching backtest runs
        """
        query = self.session.query(BacktestRun)
        
        if self._filters:
            query = query.filter(and_(*self._filters))
        
        if self._order_by is not None:
            query = query.order_by(self._order_by)
        
        if self._limit:
            query = query.limit(self._limit)
        
        return query.all()
    
    def count(self) -> int:
        """Count matching results without fetching them.
        
        Returns:
            Number of matching records
        """
        query = self.session.query(BacktestRun)
        if self._filters:
            query = query.filter(and_(*self._filters))
        return query.count()


class TradeQueryBuilder:
    """Query builder for trade data."""
    
    def __init__(self, session: Session):
        """Initialize trade query builder.
        
        Args:
            session: Database session
        """
        self.session = session
        self._filters = []
    
    def filter_by_backtest_run(self, run_id: int) -> 'TradeQueryBuilder':
        """Filter trades by backtest run.
        
        Args:
            run_id: Backtest run ID
            
        Returns:
            Self for chaining
        """
        self._filters.append(Trade.backtest_run_id == run_id)
        return self
    
    def filter_by_symbol(self, symbol: str) -> 'TradeQueryBuilder':
        """Filter by trading symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Self for chaining
        """
        self._filters.append(Trade.symbol == symbol)
        return self
    
    def filter_by_side(self, side: str) -> 'TradeQueryBuilder':
        """Filter by trade side (BUY/SELL).
        
        Args:
            side: Trade side
            
        Returns:
            Self for chaining
        """
        self._filters.append(Trade.side == side)
        return self
    
    def filter_profitable(self, profitable: bool = True) -> 'TradeQueryBuilder':
        """Filter by profitability.
        
        Args:
            profitable: True for profitable trades, False for losses
            
        Returns:
            Self for chaining
        """
        if profitable:
            self._filters.append(Trade.pnl > 0)
        else:
            self._filters.append(Trade.pnl < 0)
        return self
    
    def execute(self) -> List[Trade]:
        """Execute the query and return results.
        
        Returns:
            List of matching trades
        """
        query = self.session.query(Trade)
        if self._filters:
            query = query.filter(and_(*self._filters))
        return query.all()
    
    def aggregate_stats(self) -> Dict[str, Any]:
        """Calculate aggregate statistics for filtered trades.
        
        Returns:
            Dictionary with trade statistics
        """
        trades = self.execute()
        if not trades:
            return {}
        
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl < 0]
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / total_trades if total_trades > 0 else 0,
            'total_pnl': sum(t.pnl for t in trades if t.pnl),
            'avg_win': sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss': sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0,
        }

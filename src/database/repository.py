"""Database repository for managing backtest results."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from .models import Base, BacktestRun, Trade, PerformanceMetric


class BacktestRepository:
    """Repository pattern for database operations."""
    
    def __init__(self, database_url: str = 'sqlite:///backtests.db'):
        """
        Initialize repository with database connection.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def save_backtest_run(self, backtest_run: BacktestRun) -> BacktestRun:
        """
        Save a backtest run to database.
        
        Args:
            backtest_run: BacktestRun instance
            
        Returns:
            Saved BacktestRun with ID
        """
        session = self.get_session()
        try:
            session.add(backtest_run)
            session.commit()
            session.refresh(backtest_run)
            return backtest_run
        finally:
            session.close()
    
    def get_backtest_run(self, run_id: int) -> Optional[BacktestRun]:
        """
        Get a backtest run by ID.
        
        Args:
            run_id: Backtest run ID
            
        Returns:
            BacktestRun or None
        """
        session = self.get_session()
        try:
            return session.query(BacktestRun).filter(BacktestRun.id == run_id).first()
        finally:
            session.close()
    
    def list_backtest_runs(self, limit: int = 100) -> List[BacktestRun]:
        """
        List recent backtest runs.
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of BacktestRun objects
        """
        session = self.get_session()
        try:
            return session.query(BacktestRun).order_by(
                BacktestRun.created_at.desc()
            ).limit(limit).all()
        finally:
            session.close()
    
    def save_trades(self, trades: List[Trade]):
        """
        Save multiple trades.
        
        Args:
            trades: List of Trade instances
        """
        session = self.get_session()
        try:
            session.add_all(trades)
            session.commit()
        finally:
            session.close()
    
    def save_metrics(self, metrics: List[PerformanceMetric]):
        """
        Save performance metrics.
        
        Args:
            metrics: List of PerformanceMetric instances
        """
        session = self.get_session()
        try:
            session.add_all(metrics)
            session.commit()
        finally:
            session.close()
    
    def delete_backtest_run(self, run_id: int):
        """
        Delete a backtest run and associated data.
        
        Args:
            run_id: Backtest run ID
        """
        session = self.get_session()
        try:
            run = session.query(BacktestRun).filter(BacktestRun.id == run_id).first()
            if run:
                session.delete(run)
                session.commit()
        finally:
            session.close()

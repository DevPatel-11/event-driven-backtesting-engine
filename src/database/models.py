"""SQLAlchemy database models for storing backtest results."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class BacktestRun(Base):
    """Model for storing backtest run information."""
    __tablename__ = 'backtest_runs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    strategy_name = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)
    total_return_pct = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown_pct = Column(Float)
    win_rate_pct = Column(Float)
    total_trades = Column(Integer)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    trades = relationship("Trade", back_populates="backtest_run", cascade="all, delete-orphan")
    metrics = relationship("PerformanceMetric", back_populates="backtest_run", cascade="all, delete-orphan")


class Trade(Base):
    """Model for storing individual trades."""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    backtest_run_id = Column(Integer, ForeignKey('backtest_runs.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    pnl = Column(Float)
    
    backtest_run = relationship("BacktestRun", back_populates="trades")


class PerformanceMetric(Base):
    """Model for storing daily performance metrics."""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True)
    backtest_run_id = Column(Integer, ForeignKey('backtest_runs.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    portfolio_value = Column(Float, nullable=False)
    daily_return = Column(Float)
    cumulative_return = Column(Float)
    drawdown = Column(Float)
    
    backtest_run = relationship("BacktestRun", back_populates="metrics")

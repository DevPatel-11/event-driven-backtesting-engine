import pytest
import sys
import os
from queue import Queue
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.portfolio.portfolio import Portfolio
from src.utils.events import FillEvent, SignalEvent


def test_portfolio_initialization():
    """Test Portfolio initialization."""
    events = Queue()
    start_date = datetime(2023, 1, 1)
    initial_capital = 100000.0
    
    portfolio = Portfolio(events, start_date, initial_capital)
    
    assert portfolio.initial_capital == initial_capital
    assert portfolio.current_capital == initial_capital
    assert portfolio.current_holdings['cash'] == initial_capital
    assert portfolio.current_holdings['total'] == initial_capital


def test_update_fill_buy():
    """Test portfolio update with buy fill."""
    events = Queue()
    portfolio = Portfolio(events, datetime(2023, 1, 1), 100000.0)
    
    fill = FillEvent(
        timestamp=datetime(2023, 1, 1),
        symbol="AAPL",
        exchange="SIMULATED",
        quantity=100,
        direction="BUY",
        fill_cost=15000.0,
        commission=15.0,
        data=None
    )
    
    portfolio.update_fill(fill)
    
    assert portfolio.current_positions["AAPL"] == 100
    assert portfolio.current_holdings['cash'] < 100000.0
    assert portfolio.current_holdings['commission'] == 15.0


def test_generate_order_from_signal():
    """Test order generation from signal."""
    events = Queue()
    portfolio = Portfolio(events, datetime(2023, 1, 1), 100000.0)
    
    signal = SignalEvent(
        timestamp=datetime(2023, 1, 1),
        symbol="AAPL",
        signal_type="LONG",
        strength=1.0,
        data=None
    )
    
    portfolio.generate_order(signal)
    
    assert not events.empty()
    order = events.get()
    assert order.symbol == "AAPL"
    assert order.direction == "BUY"

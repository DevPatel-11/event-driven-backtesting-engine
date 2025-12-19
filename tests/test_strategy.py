import pytest
import sys
import os
from queue import Queue
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.strategy.base_strategy import Strategy, BuyAndHoldStrategy
from src.market_data.data_handler import CSVDataHandler
from src.utils.events import MarketEvent, EventType


def test_buy_and_hold_initialization():
    """Test BuyAndHoldStrategy initialization."""
    events = Queue()
    data = CSVDataHandler(events, "examples/data", ["AAPL"])
    strategy = BuyAndHoldStrategy(events, data)
    
    assert strategy.events == events
    assert strategy.data == data
    assert "AAPL" in strategy.bought
    assert strategy.bought["AAPL"] == False


def test_buy_and_hold_first_signal():
    """Test BuyAndHoldStrategy generates signal on first tick."""
    events = Queue()
    data = CSVDataHandler(events, "examples/data", ["AAPL"])
    strategy = BuyAndHoldStrategy(events, data)
    
    market_event = MarketEvent(
        timestamp=datetime(2023, 1, 1),
        symbol="AAPL",
        price=150.0,
        volume=1000000,
        data=None
    )
    
    signal = strategy.generate_signal(market_event)
    
    assert signal is not None
    assert signal.type == EventType.SIGNAL
    assert signal.symbol == "AAPL"
    assert signal.signal_type == "LONG"
    assert strategy.bought["AAPL"] == True


def test_buy_and_hold_no_second_signal():
    """Test BuyAndHoldStrategy does not generate second signal."""
    events = Queue()
    data = CSVDataHandler(events, "examples/data", ["AAPL"])
    strategy = BuyAndHoldStrategy(events, data)
    
    market_event = MarketEvent(
        timestamp=datetime(2023, 1, 1),
        symbol="AAPL",
        price=150.0,
        volume=1000000,
        data=None
    )
    
    # First signal
    signal1 = strategy.generate_signal(market_event)
    assert signal1 is not None
    
    # Second signal should be None
    signal2 = strategy.generate_signal(market_event)
    assert signal2 is None

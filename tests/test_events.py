import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.events import EventType, Event, MarketEvent, SignalEvent, OrderEvent, FillEvent


def test_event_types():
    """Test EventType enum values."""
    assert EventType.MARKET.value == "market"
    assert EventType.SIGNAL.value == "signal"
    assert EventType.ORDER.value == "order"
    assert EventType.FILL.value == "fill"


def test_market_event_creation():
    """Test MarketEvent creation and attributes."""
    timestamp = datetime(2023, 1, 1, 10, 0, 0)
    event = MarketEvent(
        timestamp=timestamp,
        symbol="AAPL",
        price=150.0,
        volume=1000000,
        data=None
    )
    
    assert event.type == EventType.MARKET
    assert event.timestamp == timestamp
    assert event.symbol == "AAPL"
    assert event.price == 150.0
    assert event.volume == 1000000


def test_signal_event_creation():
    """Test SignalEvent creation and attributes."""
    timestamp = datetime(2023, 1, 1, 10, 0, 0)
    event = SignalEvent(
        timestamp=timestamp,
        symbol="AAPL",
        signal_type="LONG",
        strength=1.0,
        data=None
    )
    
    assert event.type == EventType.SIGNAL
    assert event.timestamp == timestamp
    assert event.symbol == "AAPL"
    assert event.signal_type == "LONG"
    assert event.strength == 1.0


def test_order_event_creation():
    """Test OrderEvent creation and attributes."""
    timestamp = datetime(2023, 1, 1, 10, 0, 0)
    event = OrderEvent(
        timestamp=timestamp,
        symbol="AAPL",
        order_type="MKT",
        quantity=100,
        direction="BUY",
        price=None,
        data=None
    )
    
    assert event.type == EventType.ORDER
    assert event.timestamp == timestamp
    assert event.symbol == "AAPL"
    assert event.order_type == "MKT"
    assert event.quantity == 100
    assert event.direction == "BUY"
    assert event.price is None


def test_fill_event_creation():
    """Test FillEvent creation and attributes."""
    timestamp = datetime(2023, 1, 1, 10, 0, 0)
    event = FillEvent(
        timestamp=timestamp,
        symbol="AAPL",
        exchange="SIMULATED",
        quantity=100,
        direction="BUY",
        fill_cost=15000.0,
        commission=15.0,
        data=None
    )
    
    assert event.type == EventType.FILL
    assert event.timestamp == timestamp
    assert event.symbol == "AAPL"
    assert event.exchange == "SIMULATED"
    assert event.quantity == 100
    assert event.direction == "BUY"
    assert event.fill_cost == 15000.0
    assert event.commission == 15.0

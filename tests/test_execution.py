import pytest
import sys
import os
from queue import Queue
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.execution.execution import ExecutionHandler
from src.market_data.data_handler import CSVDataHandler
from src.utils.events import OrderEvent, EventType


def test_execution_handler_initialization():
    """Test ExecutionHandler initialization."""
    events = Queue()
    data = CSVDataHandler(events, "examples/data", ["AAPL"])
    
    handler = ExecutionHandler(events, data, slippage_bps=10.0, commission_pct=0.1)
    
    assert handler.events == events
    assert handler.data == data
    assert handler.slippage_bps == 10.0
    assert handler.commission_pct == 0.1


def test_create_fill_buy_order():
    """Test fill creation for buy order."""
    events = Queue()
    data = CSVDataHandler(events, "examples/data", ["AAPL"])
    handler = ExecutionHandler(events, data)
    data.update_bars()  # Load first bar
    
    order = OrderEvent(
        timestamp=datetime(2023, 1, 1),
        symbol="AAPL",
        order_type="MKT",
        quantity=100,
        direction="BUY",
        price=None,
        data=None
    )
    
    fill = handler._create_fill(order)
    
    assert fill.type == EventType.FILL
    assert fill.symbol == "AAPL"
    assert fill.quantity == 100
    assert fill.direction == "BUY"
    assert fill.fill_cost > 0
    assert fill.commission > 0


def test_slippage_applied():
    """Test that slippage is applied correctly."""
    events = Queue()
    data = CSVDataHandler(events, "examples/data", ["AAPL"])
    handler = ExecutionHandler(events, data, slippage_bps=10.0)
    
    order = OrderEvent(
        timestamp=datetime(2023, 1, 1),
        symbol="AAPL",
        order_type="MKT",
        quantity=100,
        direction="BUY",
        price=150.0,
        data=None
    )
    
    fill = handler._create_fill(order)
    
    # Buy order should have price increased by slippage
    expected_min_cost = 150.0 * 100  # Without slippage
    assert fill.fill_cost > expected_min_cost

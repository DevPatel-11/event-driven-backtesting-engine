from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime


class EventType(Enum):
    """Event types for the backtesting engine."""
    MARKET = "market"
    SIGNAL = "signal"
    ORDER = "order"
    FILL = "fill"


@dataclass
class Event:
    """Base event class with timestamp and type."""
    timestamp: datetime
    data: Any
    type: EventType = None


@dataclass
class MarketEvent(Event):
    """Market data event with symbol, price, and volume."""
    symbol: str = None
    price: float = None
    volume: int = None
    
    def __post_init__(self):
        self.type = EventType.MARKET


@dataclass
class SignalEvent(Event):
    """Trading signal event."""
    symbol: str = None
    signal_type: str = None  # 'LONG' or 'SHORT'
    strength: float = None
    
    def __post_init__(self):
        self.type = EventType.SIGNAL


@dataclass
class OrderEvent(Event):
    """Order event for execution."""
    symbol: str = None
    order_type: str = None  # 'MKT' or 'LMT'
    quantity: int = None
    direction: str = None  # 'BUY' or 'SELL'
    price: Optional[float] = None
    
    def __post_init__(self):
        self.type = EventType.ORDER


@dataclass
class FillEvent(Event):
    """Fill event representing executed order."""
    symbol: str = None
    exchange: str = None
    quantity: int = None
    direction: str = None
    fill_cost: float = None
    commission: float = None
    
    def __post_init__(self):
        self.type = EventType.FILL

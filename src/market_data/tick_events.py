"""Tick event classes for normalized market data representation."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EventType(Enum):
    """Types of tick events in the market."""
    NEW_LIMIT = "NEW_LIMIT"
    NEW_MARKET = "NEW_MARKET"
    CANCEL = "CANCEL"
    MODIFY = "MODIFY"
    TRADE = "TRADE"
    SNAPSHOT = "SNAPSHOT"


class Side(Enum):
    """Side of the order/trade."""
    BUY = "BUY"
    SELL = "SELL"
    BID = "BID"
    ASK = "ASK"


@dataclass
class TickEvent:
    """Normalized tick event for the backtesting engine."""
    timestamp_ns: int  # Nanosecond timestamp
    instrument_id: str  # Symbol/instrument identifier
    event_type: EventType  # Type of event
    price: float  # Price level
    quantity: float  # Size/volume
    side: Side  # Side of the market
    external_order_id: Optional[str] = None  # External order ID (if applicable)
    venue: Optional[str] = None  # Trading venue
    
    def to_dict(self) -> dict:
        """Convert tick event to dictionary."""
        return {
            'timestamp_ns': self.timestamp_ns,
            'instrument_id': self.instrument_id,
            'event_type': self.event_type.value,
            'price': self.price,
            'quantity': self.quantity,
            'side': self.side.value,
            'external_order_id': self.external_order_id,
            'venue': self.venue
        }

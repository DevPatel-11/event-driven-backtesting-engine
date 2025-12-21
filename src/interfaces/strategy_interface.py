"""Strategy interface - Clean separation of strategy logic."""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class SignalType(Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    CLOSE_LONG = "CLOSE_LONG"
    CLOSE_SHORT = "CLOSE_SHORT"


@dataclass
class Signal:
    """Trading signal with metadata."""
    symbol: str
    signal_type: SignalType
    quantity: float
    timestamp: float
    price: Optional[float] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class IStrategy(ABC):
    """Strategy interface - All trading strategies must implement this.
    
    This interface ensures clean separation between strategy logic
    and the rest of the backtest infrastructure.
    """
    
    @abstractmethod
    def on_market_data(self, market_data: Dict[str, Any]) -> Optional[Signal]:
        """Process incoming market data and generate trading signal.
        
        Args:
            market_data: Market data event containing price, volume, etc.
            
        Returns:
            Signal if strategy has a trade idea, None otherwise
        """
        pass
    
    @abstractmethod
    def on_fill(self, fill_event: Dict[str, Any]) -> None:
        """Handle order fill notification.
        
        Args:
            fill_event: Fill event with execution details
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset strategy state (e.g., for new backtest run)."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name for identification."""
        pass

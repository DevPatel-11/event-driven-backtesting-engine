"""Market data handler interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class MarketDataSnapshot:
    symbol: str
    timestamp: float
    bid: float
    ask: float
    last: float
    volume: float
    bid_size: Optional[float] = None
    ask_size: Optional[float] = None
    metadata: Dict[str, Any] = None

class IMarketDataHandler(ABC):
    """Market data handler interface."""
    
    @abstractmethod
    def get_latest_snapshot(self, symbol: str) -> Optional[MarketDataSnapshot]:
        """Get latest market data snapshot."""
        pass
    
    @abstractmethod
    def subscribe(self, symbols: List[str]) -> None:
        """Subscribe to market data for symbols."""
        pass
    
    @abstractmethod
    def unsubscribe(self, symbols: List[str]) -> None:
        """Unsubscribe from market data."""
        pass

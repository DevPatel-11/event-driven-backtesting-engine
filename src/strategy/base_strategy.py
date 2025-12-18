from abc import ABC, abstractmethod
from queue import Queue
from typing import Optional

from ..utils.events import MarketEvent, SignalEvent
from ..market_data.data_handler import DataHandler


class Strategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, events: Queue, data: DataHandler):
        self.events = events
        self.data = data
        self.symbol_list = data.symbol_list
    
    @abstractmethod
    def on_tick(self, event: MarketEvent) -> None:
        """Called on every market data tick."""
        raise NotImplementedError("Must implement on_tick()")
    
    @abstractmethod
    def generate_signal(self, event: MarketEvent) -> Optional[SignalEvent]:
        """Generate trading signals based on market data."""
        raise NotImplementedError("Must implement generate_signal()")


class BuyAndHoldStrategy(Strategy):
    """Simple buy and hold strategy for testing."""
    
    def __init__(self, events: Queue, data: DataHandler):
        super().__init__(events, data)
        self.bought = {symbol: False for symbol in self.symbol_list}
    
    def on_tick(self, event: MarketEvent) -> None:
        """Process market event and generate signal."""
        signal = self.generate_signal(event)
        if signal is not None:
            self.events.put(signal)
    
    def generate_signal(self, event: MarketEvent) -> Optional[SignalEvent]:
        """Generate buy signal on first tick for each symbol."""
        symbol = event.symbol
        
        if not self.bought[symbol]:
            signal = SignalEvent(
                timestamp=event.timestamp,
                symbol=symbol,
                signal_type='LONG',
                strength=1.0,
                data=None
            )
            self.bought[symbol] = True
            return signal
        
        return None

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from queue import Queue

from ..utils.events import MarketEvent


class DataHandler(ABC):
    """Abstract base class for market data handlers."""
    
    @abstractmethod
    def get_latest_bar(self, symbol: str) -> Optional[pd.Series]:
        """Get the most recent bar for a symbol."""
        raise NotImplementedError("Must implement get_latest_bar()")
    
    @abstractmethod
    def get_latest_bars(self, symbol: str, N: int = 1) -> Optional[pd.DataFrame]:
        """Get the N most recent bars for a symbol."""
        raise NotImplementedError("Must implement get_latest_bars()")
    
    @abstractmethod
    def update_bars(self) -> None:
        """Push the latest bar to the event queue."""
        raise NotImplementedError("Must implement update_bars()")


class CSVDataHandler(DataHandler):
    """Handles historical data from CSV files."""
    
    def __init__(self, events: Queue, csv_dir: str, symbol_list: List[str]):
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        
        self.symbol_data: Dict[str, pd.DataFrame] = {}
        self.latest_symbol_data: Dict[str, List[pd.Series]] = {}
        self.continue_backtest = True
        self.bar_index = 0
        
        self._load_data()
    
    def _load_data(self) -> None:
        """Load CSV data for all symbols."""
        combined_index = None
        
        for symbol in self.symbol_list:
            self.symbol_data[symbol] = pd.read_csv(
                f"{self.csv_dir}/{symbol}.csv",
                header=0,
                index_col=0,
                parse_dates=True,
                names=['datetime', 'open', 'high', 'low', 'close', 'volume']
            )
            
            if combined_index is None:
                combined_index = self.symbol_data[symbol].index
            else:
                combined_index = combined_index.union(self.symbol_data[symbol].index)
            
            self.latest_symbol_data[symbol] = []
        
        # Reindex all data to combined index
        for symbol in self.symbol_list:
            self.symbol_data[symbol] = self.symbol_data[symbol].reindex(
                index=combined_index,
                method='pad'
            ).iterrows()
    
    def get_latest_bar(self, symbol: str) -> Optional[pd.Series]:
        """Get the most recent bar."""
        try:
            return self.latest_symbol_data[symbol][-1]
        except (KeyError, IndexError):
            return None
    
    def get_latest_bars(self, symbol: str, N: int = 1) -> Optional[pd.DataFrame]:
        """Get the N most recent bars."""
        try:
            bars = self.latest_symbol_data[symbol]
            return pd.DataFrame(bars[-N:])
        except (KeyError, IndexError):
            return None
    
    def update_bars(self) -> None:
        """Push the latest bar to the event queue."""
        for symbol in self.symbol_list:
            try:
                bar = next(self.symbol_data[symbol])
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[symbol].append(bar[1])
                    
                    event = MarketEvent(
                        timestamp=bar[0],
                        symbol=symbol,
                        price=bar[1]['close'],
                        volume=bar[1]['volume'],
                        data=bar[1]
                    )
                    self.events.put(event)

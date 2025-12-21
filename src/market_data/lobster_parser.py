"""LOBSTER format parser for order book data."""

import pandas as pd
import numpy as np
from typing import Iterator, Optional, Tuple
from .tick_events import TickEvent, EventType, Side


class LobsterMessageParser:
    """Parse LOBSTER message files.
    
    LOBSTER message format (6 columns):
    - Time (seconds from midnight)
    - Event Type (1=limit, 2=cancellation, 3=deletion, 4=execution_visible, 5=execution_hidden)
    - Order ID
    - Size (number of shares)
    - Price (dollars * 10000)
    - Direction (1=buy/bid, -1=sell/ask)
    """
    
    EVENT_TYPE_MAP = {
        1: EventType.NEW_LIMIT,
        2: EventType.CANCEL,
        3: EventType.CANCEL,
        4: EventType.TRADE,
        5: EventType.TRADE
    }
    
    def __init__(self, message_file: str, symbol: str, date_str: str = None):
        """Initialize LOBSTER message parser.
        
        Args:
            message_file: Path to LOBSTER message file
            symbol: Instrument symbol
            date_str: Date string in format YYYY-MM-DD (used for timestamp calculation)
        """
        self.message_file = message_file
        self.symbol = symbol
        self.date_str = date_str
        
    def parse(self, chunk_size: int = 10000) -> Iterator[TickEvent]:
        """Parse LOBSTER messages into TickEvents.
        
        Args:
            chunk_size: Number of rows to process at a time
            
        Yields:
            TickEvent objects
        """
        # Column names for LOBSTER message file
        columns = ['time', 'event_type', 'order_id', 'size', 'price', 'direction']
        
        for chunk in pd.read_csv(self.message_file, names=columns, chunksize=chunk_size):
            for _, row in chunk.iterrows():
                yield self._row_to_tick_event(row)
    
    def _row_to_tick_event(self, row: pd.Series) -> TickEvent:
        """Convert LOBSTER message row to TickEvent."""
        # Convert seconds from midnight to nanoseconds
        timestamp_ns = int(row['time'] * 1e9)
        
        # Map event type
        event_type = self.EVENT_TYPE_MAP.get(row['event_type'], EventType.NEW_LIMIT)
        
        # Convert price from dollars * 10000 to dollars
        price = row['price'] / 10000.0
        
        # Map direction to side
        side = Side.BUY if row['direction'] == 1 else Side.SELL
        
        return TickEvent(
            timestamp_ns=timestamp_ns,
            instrument_id=self.symbol,
            event_type=event_type,
            price=price,
            quantity=float(row['size']),
            side=side,
            external_order_id=str(int(row['order_id'])),
            venue='LOBSTER'
        )


class LobsterOrderbookParser:
    """Parse LOBSTER orderbook snapshot files.
    
    LOBSTER orderbook format (4*N columns for N levels):
    - Ask Price 1, Ask Size 1, Bid Price 1, Bid Size 1, Ask Price 2, ...
    """
    
    def __init__(self, orderbook_file: str, symbol: str, num_levels: int = 10):
        """Initialize LOBSTER orderbook parser.
        
        Args:
            orderbook_file: Path to LOBSTER orderbook file
            symbol: Instrument symbol
            num_levels: Number of price levels in the orderbook
        """
        self.orderbook_file = orderbook_file
        self.symbol = symbol
        self.num_levels = num_levels
        
    def parse(self, chunk_size: int = 1000) -> Iterator[Tuple[pd.DataFrame, pd.DataFrame]]:
        """Parse LOBSTER orderbook snapshots.
        
        Args:
            chunk_size: Number of rows to process at a time
            
        Yields:
            Tuples of (bid_df, ask_df) DataFrames with columns [price, size]
        """
        # Generate column names
        columns = []
        for i in range(1, self.num_levels + 1):
            columns.extend([f'ask_price_{i}', f'ask_size_{i}', 
                          f'bid_price_{i}', f'bid_size_{i}'])
        
        for chunk in pd.read_csv(self.orderbook_file, names=columns, chunksize=chunk_size):
            for _, row in chunk.iterrows():
                yield self._row_to_orderbook(row)
    
    def _row_to_orderbook(self, row: pd.Series) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Convert LOBSTER orderbook row to bid/ask DataFrames."""
        bids = []
        asks = []
        
        for i in range(1, self.num_levels + 1):
            # Extract bid data
            bid_price = row[f'bid_price_{i}'] / 10000.0
            bid_size = row[f'bid_size_{i}']
            if bid_price > 0 and bid_size > 0:
                bids.append({'price': bid_price, 'size': bid_size, 'level': i})
            
            # Extract ask data
            ask_price = row[f'ask_price_{i}'] / 10000.0
            ask_size = row[f'ask_size_{i}']
            if ask_price > 0 and ask_size > 0:
                asks.append({'price': ask_price, 'size': ask_size, 'level': i})
        
        bid_df = pd.DataFrame(bids) if bids else pd.DataFrame(columns=['price', 'size', 'level'])
        ask_df = pd.DataFrame(asks) if asks else pd.DataFrame(columns=['price', 'size', 'level'])
        
        return bid_df, ask_df

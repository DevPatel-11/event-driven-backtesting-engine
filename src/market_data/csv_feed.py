"""CSV feed parser with configurable schema."""

import pandas as pd
from typing import Iterator, Dict, Optional, Callable
from datetime import datetime
from .tick_events import TickEvent, EventType, Side


class CSVFeedConfig:
    """Configuration for CSV feed parsing."""
    
    def __init__(self,
                 timestamp_col: str = 'timestamp',
                 symbol_col: str = 'symbol',
                 price_col: str = 'price',
                 quantity_col: str = 'quantity',
                 side_col: str = 'side',
                 event_type_col: Optional[str] = None,
                 timestamp_format: Optional[str] = None,
                 timestamp_unit: str = 'ns',  # 's', 'ms', 'us', 'ns'
                 price_scale: float = 1.0,
                 quantity_scale: float = 1.0,
                 side_map: Optional[Dict[str, Side]] = None,
                 event_type_map: Optional[Dict[str, EventType]] = None,
                 venue: str = 'CSV'):
        """Initialize CSV feed configuration.
        
        Args:
            timestamp_col: Name of timestamp column
            symbol_col: Name of symbol/instrument column  
            price_col: Name of price column
            quantity_col: Name of quantity/volume column
            side_col: Name of side column
            event_type_col: Name of event type column (optional)
            timestamp_format: Format string for parsing timestamps (e.g., '%Y-%m-%d %H:%M:%S')
            timestamp_unit: Unit of timestamp ('s', 'ms', 'us', 'ns')
            price_scale: Multiplier for price (e.g., 0.01 if prices are in cents)
            quantity_scale: Multiplier for quantity
            side_map: Dict mapping string values to Side enum
            event_type_map: Dict mapping string values to EventType enum
            venue: Venue name
        """
        self.timestamp_col = timestamp_col
        self.symbol_col = symbol_col
        self.price_col = price_col
        self.quantity_col = quantity_col
        self.side_col = side_col
        self.event_type_col = event_type_col
        self.timestamp_format = timestamp_format
        self.timestamp_unit = timestamp_unit
        self.price_scale = price_scale
        self.quantity_scale = quantity_scale
        self.venue = venue
        
        # Default side mapping
        if side_map is None:
            self.side_map = {
                'BUY': Side.BUY, 'buy': Side.BUY, '1': Side.BUY, 'B': Side.BUY,
                'SELL': Side.SELL, 'sell': Side.SELL, '-1': Side.SELL, 'S': Side.SELL,
                'BID': Side.BID, 'bid': Side.BID,
                'ASK': Side.ASK, 'ask': Side.ASK, 'OFFER': Side.ASK
            }
        else:
            self.side_map = side_map
        
        # Default event type mapping
        if event_type_map is None:
            self.event_type_map = {
                'TRADE': EventType.TRADE, 'trade': EventType.TRADE,
                'NEW': EventType.NEW_LIMIT, 'new': EventType.NEW_LIMIT,
                'CANCEL': EventType.CANCEL, 'cancel': EventType.CANCEL,
                'MODIFY': EventType.MODIFY, 'modify': EventType.MODIFY,
                'SNAPSHOT': EventType.SNAPSHOT, 'snapshot': EventType.SNAPSHOT
            }
        else:
            self.event_type_map = event_type_map


class CSVFeed:
    """CSV feed parser with configurable schema."""
    
    def __init__(self, file_path: str, config: CSVFeedConfig):
        """Initialize CSV feed parser.
        
        Args:
            file_path: Path to CSV file
            config: CSVFeedConfig object
        """
        self.file_path = file_path
        self.config = config
        
    def parse(self, chunk_size: int = 10000, 
              filter_symbol: Optional[str] = None) -> Iterator[TickEvent]:
        """Parse CSV file into TickEvents.
        
        Args:
            chunk_size: Number of rows to process at a time
            filter_symbol: Only return events for this symbol (optional)
            
        Yields:
            TickEvent objects
        """
        for chunk in pd.read_csv(self.file_path, chunksize=chunk_size):
            # Filter by symbol if specified
            if filter_symbol:
                chunk = chunk[chunk[self.config.symbol_col] == filter_symbol]
            
            for _, row in chunk.iterrows():
                try:
                    yield self._row_to_tick_event(row)
                except Exception as e:
                    # Skip malformed rows
                    continue
    
    def _row_to_tick_event(self, row: pd.Series) -> TickEvent:
        """Convert CSV row to TickEvent."""
        # Parse timestamp
        timestamp_ns = self._parse_timestamp(row[self.config.timestamp_col])
        
        # Parse price and quantity with scaling
        price = float(row[self.config.price_col]) * self.config.price_scale
        quantity = float(row[self.config.quantity_col]) * self.config.quantity_scale
        
        # Parse side
        side_value = str(row[self.config.side_col])
        side = self.config.side_map.get(side_value, Side.BUY)
        
        # Parse event type if available
        if self.config.event_type_col and self.config.event_type_col in row.index:
            event_type_value = str(row[self.config.event_type_col])
            event_type = self.config.event_type_map.get(event_type_value, EventType.TRADE)
        else:
            event_type = EventType.TRADE  # Default to TRADE
        
        return TickEvent(
            timestamp_ns=timestamp_ns,
            instrument_id=str(row[self.config.symbol_col]),
            event_type=event_type,
            price=price,
            quantity=quantity,
            side=side,
            venue=self.config.venue
        )
    
    def _parse_timestamp(self, timestamp_value) -> int:
        """Parse timestamp to nanoseconds."""
        if isinstance(timestamp_value, str) and self.config.timestamp_format:
            # Parse string timestamp
            dt = datetime.strptime(timestamp_value, self.config.timestamp_format)
            return int(dt.timestamp() * 1e9)
        else:
            # Numeric timestamp - convert to nanoseconds
            ts_float = float(timestamp_value)
            
            if self.config.timestamp_unit == 's':
                return int(ts_float * 1e9)
            elif self.config.timestamp_unit == 'ms':
                return int(ts_float * 1e6)
            elif self.config.timestamp_unit == 'us':
                return int(ts_float * 1e3)
            else:  # 'ns'
                return int(ts_float)

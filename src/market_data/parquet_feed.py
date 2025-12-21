"""Parquet feed parser for efficient large-scale historical data."""

import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
from typing import Iterator, Optional, List
from .tick_events import TickEvent, EventType, Side
from .csv_feed import CSVFeedConfig


class ParquetFeed:
    """Parquet feed parser for columnar tick data.
    
    Canonical schema:
    - timestamp_ns: int64 (nanoseconds)
    - symbol: string
    - side: string (BUY/SELL/BID/ASK)
    - price: float64
    - size: float64
    - event_type: string (optional)
    - venue: string (optional)
    """
    
    def __init__(self, file_path: str, config: Optional[CSVFeedConfig] = None):
        """Initialize Parquet feed parser.
        
        Args:
            file_path: Path to Parquet file
            config: Optional CSVFeedConfig for column mapping
        """
        self.file_path = file_path
        self.config = config or CSVFeedConfig()  # Use default if not provided
        self.parquet_file = pq.ParquetFile(file_path)
        
    def parse(self,
              batch_size: int = 10000,
              filter_symbol: Optional[str] = None,
              start_time_ns: Optional[int] = None,
              end_time_ns: Optional[int] = None) -> Iterator[TickEvent]:
        """Parse Parquet file into TickEvents with optional filtering.
        
        Args:
            batch_size: Number of rows to read per batch
            filter_symbol: Only return events for this symbol
            start_time_ns: Start timestamp in nanoseconds (inclusive)
            end_time_ns: End timestamp in nanoseconds (exclusive)
            
        Yields:
            TickEvent objects
        """
        # Build filter expression for predicate pushdown
        filters = []
        
        if filter_symbol:
            filters.append((self.config.symbol_col, '=', filter_symbol))
        
        if start_time_ns is not None:
            filters.append((self.config.timestamp_col, '>=', start_time_ns))
        
        if end_time_ns is not None:
            filters.append((self.config.timestamp_col, '<', end_time_ns))
        
        # Read in batches
        for batch in self.parquet_file.iter_batches(batch_size=batch_size):
            df = batch.to_pandas()
            
            # Apply filters if predicate pushdown not supported
            if filter_symbol and self.config.symbol_col in df.columns:
                df = df[df[self.config.symbol_col] == filter_symbol]
            
            if start_time_ns is not None and self.config.timestamp_col in df.columns:
                df = df[df[self.config.timestamp_col] >= start_time_ns]
            
            if end_time_ns is not None and self.config.timestamp_col in df.columns:
                df = df[df[self.config.timestamp_col] < end_time_ns]
            
            for _, row in df.iterrows():
                try:
                    yield self._row_to_tick_event(row)
                except Exception as e:
                    continue
    
    def _row_to_tick_event(self, row: pd.Series) -> TickEvent:
        """Convert Parquet row to TickEvent."""
        # Get timestamp (already in nanoseconds)
        timestamp_ns = int(row[self.config.timestamp_col])
        
        # Parse price and quantity
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
            event_type = EventType.TRADE
        
        # Get venue if available
        venue = row.get('venue', self.config.venue) if 'venue' in row.index else self.config.venue
        
        return TickEvent(
            timestamp_ns=timestamp_ns,
            instrument_id=str(row[self.config.symbol_col]),
            event_type=event_type,
            price=price,
            quantity=quantity,
            side=side,
            venue=venue
        )
    
    @staticmethod
    def write_parquet(df: pd.DataFrame, output_path: str,
                     compression: str = 'snappy',
                     row_group_size: int = 100000):
        """Write DataFrame to Parquet format.
        
        Args:
            df: DataFrame with tick data
            output_path: Output file path
            compression: Compression codec ('snappy', 'gzip', 'brotli', 'lz4', 'zstd')
            row_group_size: Number of rows per row group
        """
        table = pa.Table.from_pandas(df)
        pq.write_table(
            table,
            output_path,
            compression=compression,
            row_group_size=row_group_size,
            use_dictionary=True
        )

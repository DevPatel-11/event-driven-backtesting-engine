"""Example: Parse Parquet tick data with time-range filtering."""

from src.market_data.parquet_feed import ParquetFeed
from src.market_data.csv_feed import CSVFeedConfig

def main():
    # Optional: customize column names if different from defaults
    config = CSVFeedConfig(
        timestamp_col='timestamp_ns',
        symbol_col='symbol',
        price_col='price',
        quantity_col='size',
        side_col='side',
        venue='Crypto'
    )
    
    # Parse Parquet file with filtering
    feed = ParquetFeed('path/to/tick_data.parquet', config)
    
    # Example: Filter by symbol and time range
    start_time = int(1640995200 * 1e9)  # 2022-01-01 00:00:00 in nanoseconds
    end_time = int(1641081600 * 1e9)    # 2022-01-02 00:00:00 in nanoseconds
    
    for i, tick_event in enumerate(feed.parse(
        batch_size=10000,
        filter_symbol='BTC-USD',
        start_time_ns=start_time,
        end_time_ns=end_time
    )):
        if i >= 10:
            break
        print(f"Tick {i}: {tick_event.to_dict()}")

if __name__ == '__main__':
    main()
EOFcat requirements.txt
echo 'pyarrow>=10.0.0' >> requirements.txt
cat > docs/DATA_FORMATS.md << 'EOF'
# Supported Data Formats

The backtesting engine supports realistic tick data formats commonly used in HFT and quantitative trading.

## Overview

All feed parsers convert raw data into a normalized `TickEvent` format:

```python
@dataclass
class TickEvent:
    timestamp_ns: int          # Nanosecond timestamp
    instrument_id: str         # Symbol/instrument identifier
    event_type: EventType      # NEW_LIMIT, CANCEL, MODIFY, TRADE, SNAPSHOT
    price: float              # Price level
    quantity: float           # Size/volume
    side: Side                # BUY, SELL, BID, ASK
    external_order_id: Optional[str] = None
    venue: Optional[str] = None
```

## LOBSTER Format

**LOBSTER** (Limit Order Book System - The Efficient Reconstructor) provides high-quality limit order book data for NASDAQ stocks.

### Message File Format
6 columns:
- Time (seconds from midnight)
- Event Type (1=limit, 2=cancel, 3=delete, 4=exec_visible, 5=exec_hidden)
- Order ID
- Size (shares)
- Price (dollars × 10000)
- Direction (1=buy, -1=sell)

### Orderbook File Format
4N columns for N levels:
- Ask Price 1, Ask Size 1, Bid Price 1, Bid Size 1, Ask Price 2, ...

### Usage Example

```python
from src.market_data.lobster_parser import LobsterMessageParser

parser = LobsterMessageParser(
    message_file='AAPL_2023-01-01_message.csv',
    symbol='AAPL',
    date_str='2023-01-01'
)

for tick_event in parser.parse(chunk_size=10000):
    # Process tick events
    print(tick_event.to_dict())
```

## CSV Format (Configurable Schema)

Supports arbitrary CSV schemas with column mapping.

### Configuration Options

- **Column mapping**: timestamp, symbol, price, quantity, side, event_type
- **Timestamp formats**: Unix (s/ms/us/ns) or datetime strings
- **Price/quantity scaling**: Handle data in cents, basis points, etc.
- **Side mapping**: Flexible string → Side enum mapping
- **Event type mapping**: Map custom event names to EventType

### Usage Example

```python
from src.market_data.csv_feed import CSVFeed, CSVFeedConfig

config = CSVFeedConfig(
    timestamp_col='time',
    symbol_col='ticker',
    price_col='price',
    quantity_col='volume',
    side_col='side',
    timestamp_unit='ms',
    price_scale=0.01,  # Prices in cents
    venue='NYSE'
)

feed = CSVFeed('tick_data.csv', config)
for tick_event in feed.parse(chunk_size=5000, filter_symbol='AAPL'):
    # Process events
    pass
```

## Parquet Format (Columnar Storage)

**Parquet** provides efficient columnar storage ideal for large historical datasets.

### Canonical Schema

```python
{
    'timestamp_ns': 'int64',      # Nanosecond timestamps
    'symbol': 'string',
    'side': 'string',             # BUY/SELL/BID/ASK
    'price': 'float64',
    'size': 'float64',
    'event_type': 'string',       # Optional
    'venue': 'string'             # Optional
}
```

### Features

- **Predicate pushdown**: Filter by symbol/time range at read time
- **Compression**: snappy, gzip, brotli, lz4, zstd
- **Batch reading**: Process large files in chunks
- **Columnar scans**: Efficient for time-series queries

### Usage Example

```python
from src.market_data.parquet_feed import ParquetFeed

feed = ParquetFeed('tick_data.parquet')

# Filter by symbol and time range
start_time_ns = int(1640995200 * 1e9)  # 2022-01-01
end_time_ns = int(1641081600 * 1e9)    # 2022-01-02

for tick_event in feed.parse(
    batch_size=10000,
    filter_symbol='BTC-USD',
    start_time_ns=start_time_ns,
    end_time_ns=end_time_ns
):
    # Process events
    pass
```

### Writing Parquet Files

```python
import pandas as pd
from src.market_data.parquet_feed import ParquetFeed

df = pd.DataFrame({
    'timestamp_ns': [...],
    'symbol': [...],
    'side': [...],
    'price': [...],
    'size': [...]
})

ParquetFeed.write_parquet(
    df,
    'output.parquet',
    compression='snappy',
    row_group_size=100000
)
```

## Crypto L1/L2 Feeds

Use the CSV or Parquet parsers with appropriate column mappings:

**L1 (Top-of-book)**:
- timestamp, symbol, bid_price, bid_size, ask_price, ask_size, last_trade_price, last_trade_size

**L2 (Order book depth)**:
- timestamp, symbol, side, price, size, level

## Performance Tips

1. **Chunk size**: Tune based on available memory (10K-100K rows typical)
2. **Parquet for large datasets**: 10-100x faster than CSV for filtered reads
3. **Symbol filtering**: Apply early to reduce memory usage
4. **Time-range filtering**: Use Parquet predicate pushdown when possible

## Integration with Backtesting Engine

Feed parsers generate `TickEvent` objects that can be:
1. Fed directly into the event queue
2. Converted to `MarketEvent` for the backtesting engine
3. Used to reconstruct order book state

See `examples/data_feeds/` for complete integration examples.
EOFcat >> README.md << 'EOF'

## Data Formats Support

The engine supports realistic tick data formats used in HFT and quantitative trading:

- **LOBSTER**: NASDAQ limit order book data (message + orderbook files)
- **CSV with configurable schema**: Flexible column mapping for arbitrary CSV formats
- **Parquet**: Efficient columnar storage for large historical datasets

### Quick Example

```python
from src.market_data.lobster_parser import LobsterMessageParser

# Parse LOBSTER data
parser = LobsterMessageParser(
    message_file='AAPL_2023-01-01_message.csv',
    symbol='AAPL'
)

for tick_event in parser.parse(chunk_size=10000):
    # TickEvent with normalized fields:
    # timestamp_ns, instrument_id, event_type, price, quantity, side
    process_tick(tick_event)
```

See [`docs/DATA_FORMATS.md`](docs/DATA_FORMATS.md) for complete documentation on:
- LOBSTER message/orderbook parsing
- CSV schema configuration
- Parquet batch processing with filtering
- Crypto L1/L2 feed examples
- Performance tips

**Examples**: Check `examples/data_feeds/` for ready-to-run scripts.

"""Example: Parse CSV tick data with custom schema."""

from src.market_data.csv_feed import CSVFeed, CSVFeedConfig

def main():
    # Create configuration for your CSV format
    config = CSVFeedConfig(
        timestamp_col='time',
        symbol_col='ticker',
        price_col='price',
        quantity_col='volume',
        side_col='side',
        event_type_col='type',
        timestamp_unit='ms',  # Timestamps in milliseconds
        price_scale=1.0,
        venue='NYSE'
    )
    
    # Parse CSV file
    feed = CSVFeed('path/to/tick_data.csv', config)
    
    # Process events
    for i, tick_event in enumerate(feed.parse(chunk_size=5000)):
        if i >= 10:
            break
        print(f"Tick {i}: {tick_event.to_dict()}")

if __name__ == '__main__':
    main()

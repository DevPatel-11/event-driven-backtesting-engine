"""Example: Parse LOBSTER data format."""

from src.market_data.lobster_parser import LobsterMessageParser

def main():
    # Example LOBSTER message file parsing
    parser = LobsterMessageParser(
        message_file='path/to/AAPL_2023-01-01_message.csv',
        symbol='AAPL',
        date_str='2023-01-01'
    )
    
    # Parse and print first 10 tick events
    for i, tick_event in enumerate(parser.parse(chunk_size=1000)):
        if i >= 10:
            break
        print(f"Tick {i}: {tick_event.to_dict()}")

if __name__ == '__main__':
    main()

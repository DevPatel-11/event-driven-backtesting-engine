"""
Mean Reversion Strategy

Trades based on deviation from moving average.
Buys when price drops below mean, sells when above.
"""

from typing import Dict, Optional, List
from collections import deque
import numpy as np
from src.interfaces.strategy_interface import StrategyInterface


class MeanReversionStrategy(StrategyInterface):
    """
    Mean reversion strategy using Bollinger Bands.
    """
    
    def __init__(self, window: int = 20, num_std: float = 2.0, position_size: int = 100):
        """
        Args:
            window: Lookback window for moving average
            num_std: Number of standard deviations for bands
            position_size: Size of each trade
        """
        self.window = window
        self.num_std = num_std
        self.position_size = position_size
        self.price_history = deque(maxlen=window)
        self.position = 0
        self.entry_price = None
        
    def on_market_data(self, data: Dict) -> Optional[Dict]:
        """
        Generate signals based on mean reversion.
        
        Returns:
            Order dict if signal generated, None otherwise
        """
        mid_price = (data['bid'] + data['ask']) / 2
        self.price_history.append(mid_price)
        
        # Need enough history
        if len(self.price_history) < self.window:
            return None
            
        # Calculate Bollinger Bands
        prices = np.array(self.price_history)
        sma = np.mean(prices)
        std = np.std(prices)
        
        upper_band = sma + (self.num_std * std)
        lower_band = sma - (self.num_std * std)
        
        # Generate signals
        order = None
        
        # Price below lower band and no position -> BUY
        if mid_price < lower_band and self.position == 0:
            order = {
                'symbol': data['symbol'],
                'side': 'BUY',
                'quantity': self.position_size,
                'price': data['ask'],  # Market taker
                'order_type': 'MARKET',
                'strategy': 'MeanReversion'
            }
            self.position = self.position_size
            self.entry_price = mid_price
            
        # Price above upper band and no position -> SELL
        elif mid_price > upper_band and self.position == 0:
            order = {
                'symbol': data['symbol'],
                'side': 'SELL',
                'quantity': self.position_size,
                'price': data['bid'],
                'order_type': 'MARKET',
                'strategy': 'MeanReversion'
            }
            self.position = -self.position_size
            self.entry_price = mid_price
            
        # Close long position when price crosses above SMA
        elif self.position > 0 and mid_price > sma:
            order = {
                'symbol': data['symbol'],
                'side': 'SELL',
                'quantity': self.position,
                'price': data['bid'],
                'order_type': 'MARKET',
                'strategy': 'MeanReversion'
            }
            self.position = 0
            self.entry_price = None
            
        # Close short position when price crosses below SMA
        elif self.position < 0 and mid_price < sma:
            order = {
                'symbol': data['symbol'],
                'side': 'BUY',
                'quantity': abs(self.position),
                'price': data['ask'],
                'order_type': 'MARKET',
                'strategy': 'MeanReversion'
            }
            self.position = 0
            self.entry_price = None
            
        return order
    
    def on_fill(self, fill: Dict) -> None:
        """Handle fill notification."""
        pass
    
    def get_state(self) -> Dict:
        """Return strategy state."""
        if len(self.price_history) >= self.window:
            prices = np.array(self.price_history)
            sma = np.mean(prices)
            std = np.std(prices)
        else:
            sma = None
            std = None
            
        return {
            'position': self.position,
            'entry_price': self.entry_price,
            'sma': sma,
            'std': std,
            'samples': len(self.price_history)
        }

"""
Statistical Arbitrage (Pairs Trading) Strategy

Trades based on mean-reverting spread between correlated assets.
Long underperformer, short outperformer.
"""

from typing import Dict, Optional, Tuple
from collections import deque
import numpy as np
from interfaces.strategy_interface import StrategyInterface


class StatisticalArbitrageStrategy(StrategyInterface):
    """
    Pairs trading strategy based on cointegration.
    """
    
    def __init__(self, symbol_pair: Tuple[str, str], window: int = 30, 
                 entry_threshold: float = 2.0, exit_threshold: float = 0.5,
                 position_size: int = 100):
        """
        Args:
            symbol_pair: Tuple of two cointegrated symbols
            window: Lookback window for spread calculation
            entry_threshold: Z-score threshold to enter position
            exit_threshold: Z-score threshold to exit position
            position_size: Size of each leg
        """
        self.symbol_a, self.symbol_b = symbol_pair
        self.window = window
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.position_size = position_size
        
        self.spread_history = deque(maxlen=window)
        self.price_a_history = deque(maxlen=window)
        self.price_b_history = deque(maxlen=window)
        
        self.position_a = 0
        self.position_b = 0
        self.hedge_ratio = 1.0  # Will be calculated from historical data
        
        # Track latest prices
        self.latest_price_a = None
        self.latest_price_b = None
        
    def on_market_data(self, data: Dict) -> Optional[Dict]:
        """
        Generate pairs trade signals.
        
        Returns:
            Order dict if signal generated, None otherwise
        """
        symbol = data['symbol']
        mid_price = (data['bid'] + data['ask']) / 2
        
        # Update price tracking
        if symbol == self.symbol_a:
            self.latest_price_a = mid_price
            self.price_a_history.append(mid_price)
        elif symbol == self.symbol_b:
            self.latest_price_b = mid_price
            self.price_b_history.append(mid_price)
        else:
            return None  # Not our pair
            
        # Need both prices
        if self.latest_price_a is None or self.latest_price_b is None:
            return None
            
        # Calculate spread
        spread = self.latest_price_a - (self.hedge_ratio * self.latest_price_b)
        self.spread_history.append(spread)
        
        # Need enough history
        if len(self.spread_history) < self.window:
            return None
            
        # Calculate z-score
        spreads = np.array(self.spread_history)
        mean_spread = np.mean(spreads)
        std_spread = np.std(spreads)
        
        if std_spread == 0:
            return None
            
        z_score = (spread - mean_spread) / std_spread
        
        # Generate signals
        order = None
        
        # Spread too high: Short A, Long B
        if z_score > self.entry_threshold and self.position_a == 0:
            # Return order for current symbol
            if symbol == self.symbol_a:
                order = {
                    'symbol': self.symbol_a,
                    'side': 'SELL',
                    'quantity': self.position_size,
                    'price': data['bid'],
                    'order_type': 'MARKET',
                    'strategy': 'StatArb'
                }
                self.position_a = -self.position_size
            elif symbol == self.symbol_b:
                order = {
                    'symbol': self.symbol_b,
                    'side': 'BUY',
                    'quantity': int(self.position_size * self.hedge_ratio),
                    'price': data['ask'],
                    'order_type': 'MARKET',
                    'strategy': 'StatArb'
                }
                self.position_b = int(self.position_size * self.hedge_ratio)
                
        # Spread too low: Long A, Short B
        elif z_score < -self.entry_threshold and self.position_a == 0:
            if symbol == self.symbol_a:
                order = {
                    'symbol': self.symbol_a,
                    'side': 'BUY',
                    'quantity': self.position_size,
                    'price': data['ask'],
                    'order_type': 'MARKET',
                    'strategy': 'StatArb'
                }
                self.position_a = self.position_size
            elif symbol == self.symbol_b:
                order = {
                    'symbol': self.symbol_b,
                    'side': 'SELL',
                    'quantity': int(self.position_size * self.hedge_ratio),
                    'price': data['bid'],
                    'order_type': 'MARKET',
                    'strategy': 'StatArb'
                }
                self.position_b = -int(self.position_size * self.hedge_ratio)
                
        # Exit when spread reverts
        elif abs(z_score) < self.exit_threshold and self.position_a != 0:
            if symbol == self.symbol_a and self.position_a > 0:
                order = {
                    'symbol': self.symbol_a,
                    'side': 'SELL',
                    'quantity': self.position_a,
                    'price': data['bid'],
                    'order_type': 'MARKET',
                    'strategy': 'StatArb'
                }
                self.position_a = 0
            elif symbol == self.symbol_a and self.position_a < 0:
                order = {
                    'symbol': self.symbol_a,
                    'side': 'BUY',
                    'quantity': abs(self.position_a),
                    'price': data['ask'],
                    'order_type': 'MARKET',
                    'strategy': 'StatArb'
                }
                self.position_a = 0
            elif symbol == self.symbol_b and self.position_b > 0:
                order = {
                    'symbol': self.symbol_b,
                    'side': 'SELL',
                    'quantity': self.position_b,
                    'price': data['bid'],
                    'order_type': 'MARKET',
                    'strategy': 'StatArb'
                }
                self.position_b = 0
            elif symbol == self.symbol_b and self.position_b < 0:
                order = {
                    'symbol': self.symbol_b,
                    'side': 'BUY',
                    'quantity': abs(self.position_b),
                    'price': data['ask'],
                    'order_type': 'MARKET',
                    'strategy': 'StatArb'
                }
                self.position_b = 0
                
        return order
    
    def on_fill(self, fill: Dict) -> None:
        """Handle fill notification."""
        pass
    
    def get_state(self) -> Dict:
        """Return strategy state."""
        if len(self.spread_history) >= self.window:
            spreads = np.array(self.spread_history)
            mean_spread = np.mean(spreads)
            std_spread = np.std(spreads)
            current_spread = spreads[-1]
            z_score = (current_spread - mean_spread) / std_spread if std_spread > 0 else 0
        else:
            z_score = None
            
        return {
            'position_a': self.position_a,
            'position_b': self.position_b,
            'z_score': z_score,
            'hedge_ratio': self.hedge_ratio,
            'samples': len(self.spread_history)
        }

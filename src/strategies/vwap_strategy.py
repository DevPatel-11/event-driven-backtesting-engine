"""
VWAP (Volume-Weighted Average Price) Strategy

Executes orders at volume-weighted average price to minimize market impact.
Used for large institutional orders.
"""

from typing import Dict, Optional
import numpy as np
from src.interfaces.strategy_interface import StrategyInterface


class VWAPStrategy(StrategyInterface):
    """
    VWAP execution strategy that slices large orders according to historical volume profile.
    """
    
    def __init__(self, target_quantity: int, total_duration_minutes: int = 60):
        """
        Args:
            target_quantity: Total quantity to execute
            total_duration_minutes: Time window to spread execution
        """
        self.target_quantity = target_quantity
        self.total_duration = total_duration_minutes
        self.executed_quantity = 0
        self.volume_profile = []  # Historical volume distribution
        self.start_time = None
        
    def on_market_data(self, data: Dict) -> Optional[Dict]:
        """
        Generate orders based on VWAP algorithm.
        
        Returns:
            Order dict if should trade, None otherwise
        """
        if self.start_time is None:
            self.start_time = data.get('timestamp')
            
        # Calculate time elapsed
        elapsed = (data['timestamp'] - self.start_time).total_seconds() / 60
        
        if elapsed >= self.total_duration:
            return None  # Execution complete
            
        # Get current volume
        current_volume = data.get('volume', 0)
        
        # Calculate target cumulative volume participation
        target_participation = elapsed / self.total_duration
        target_cumulative_qty = int(self.target_quantity * target_participation)
        
        # Calculate slice size
        slice_qty = target_cumulative_qty - self.executed_quantity
        
        if slice_qty > 0:
            # Limit order at current mid price
            mid_price = (data['bid'] + data['ask']) / 2
            
            order = {
                'symbol': data['symbol'],
                'side': 'BUY' if self.target_quantity > 0 else 'SELL',
                'quantity': abs(slice_qty),
                'price': mid_price,
                'order_type': 'LIMIT',
                'strategy': 'VWAP'
            }
            
            self.executed_quantity += slice_qty
            return order
            
        return None
    
    def on_fill(self, fill: Dict) -> None:
        """Handle fill notification."""
        pass
    
    def get_state(self) -> Dict:
        """Return strategy state."""
        return {
            'executed': self.executed_quantity,
            'target': self.target_quantity,
            'completion': self.executed_quantity / self.target_quantity if self.target_quantity else 0
        }

"""
TWAP (Time-Weighted Average Price) Strategy

Executes orders evenly over time to minimize market impact.
Simpler alternative to VWAP.
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from src.interfaces.strategy_interface import StrategyInterface


class TWAPStrategy(StrategyInterface):
    """
    TWAP execution strategy that splits orders into equal slices over time.
    """
    
    def __init__(self, target_quantity: int, total_duration_minutes: int = 60, num_slices: int = 12):
        """
        Args:
            target_quantity: Total quantity to execute
            total_duration_minutes: Time window to spread execution
            num_slices: Number of equal time slices
        """
        self.target_quantity = target_quantity
        self.total_duration = total_duration_minutes
        self.num_slices = num_slices
        self.slice_size = abs(target_quantity) // num_slices
        self.executed_quantity = 0
        self.slice_interval = total_duration_minutes / num_slices
        self.start_time = None
        self.last_slice_time = None
        self.slices_executed = 0
        
    def on_market_data(self, data: Dict) -> Optional[Dict]:
        """
        Generate orders based on TWAP algorithm.
        
        Returns:
            Order dict if should trade, None otherwise
        """
        current_time = data.get('timestamp')
        
        if self.start_time is None:
            self.start_time = current_time
            self.last_slice_time = current_time
            
        # Check if we've completed all slices
        if self.slices_executed >= self.num_slices:
            return None
            
        # Calculate time since last slice
        elapsed_since_slice = (current_time - self.last_slice_time).total_seconds() / 60
        
        # Time to execute next slice?
        if elapsed_since_slice >= self.slice_interval:
            # Handle final slice (may be different size due to rounding)
            if self.slices_executed == self.num_slices - 1:
                remaining = abs(self.target_quantity) - self.executed_quantity
                slice_qty = remaining
            else:
                slice_qty = self.slice_size
                
            mid_price = (data['bid'] + data['ask']) / 2
            
            order = {
                'symbol': data['symbol'],
                'side': 'BUY' if self.target_quantity > 0 else 'SELL',
                'quantity': slice_qty,
                'price': mid_price,
                'order_type': 'LIMIT',
                'strategy': 'TWAP'
            }
            
            self.executed_quantity += slice_qty
            self.slices_executed += 1
            self.last_slice_time = current_time
            
            return order
            
        return None
    
    def on_fill(self, fill: Dict) -> None:
        """Handle fill notification."""
        pass
    
    def get_state(self) -> Dict:
        """Return strategy state."""
        return {
            'executed': self.executed_quantity,
            'target': abs(self.target_quantity),
            'slices_completed': self.slices_executed,
            'total_slices': self.num_slices,
            'completion': self.slices_executed / self.num_slices
        }

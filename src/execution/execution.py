from queue import Queue
from datetime import datetime
from typing import Optional

from ..utils.events import FillEvent, OrderEvent
from ..market_data.data_handler import DataHandler


class ExecutionHandler:
    """Simulates order execution with slippage and costs."""
    
    def __init__(self, events: Queue, data: DataHandler, slippage_bps: float = 10.0, commission_pct: float = 0.1):
        self.events = events
        self.data = data
        self.slippage_bps = slippage_bps  # basis points (1 bp = 0.01%)
        self.commission_pct = commission_pct  # percentage (e.g., 0.1 = 0.1%)
    
    def execute_order(self, event: OrderEvent) -> None:
        """Process order events and generate fill events."""
        if event.type.value == 'order':
            fill_event = self._create_fill(event)
            self.events.put(fill_event)
    
    def _create_fill(self, order: OrderEvent) -> FillEvent:
        """Simulate order fills with slippage and commission."""
        # Get current market price
        bar = self.data.get_latest_bar(order.symbol)
        if bar is not None:
            fill_price = bar['close']
        else:
            fill_price = order.price if order.price is not None else 0.0
        
        # Apply slippage model (basis points)
        slippage_factor = self.slippage_bps / 10000.0  # convert bp to decimal
        if order.direction == 'BUY':
            fill_price *= (1 + slippage_factor)
        else:  # SELL
            fill_price *= (1 - slippage_factor)
        
        # Calculate fill cost
        fill_cost = fill_price * order.quantity
        
        # Calculate commission (percentage of trade value)
        commission = fill_cost * (self.commission_pct / 100.0)
        
        # Create fill event
        fill = FillEvent(
            timestamp=datetime.now(),
            symbol=order.symbol,
            exchange='SIMULATED',
            quantity=order.quantity,
            direction=order.direction,
            fill_cost=fill_cost,
            commission=commission,
            data=None
        )
        
        return fill

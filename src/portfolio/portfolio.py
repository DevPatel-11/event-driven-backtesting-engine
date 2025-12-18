import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from queue import Queue

from ..utils.events import FillEvent, OrderEvent, SignalEvent


class Portfolio:
    """Handles position tracking and PnL calculation."""
    
    def __init__(self, events: Queue, start_date: datetime, initial_capital: float = 100000.0):
        self.events = events
        self.start_date = start_date
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        self.all_positions: List[Dict] = []
        self.current_positions: Dict[str, int] = {}
        self.all_holdings: List[Dict] = []
        self.current_holdings: Dict[str, float] = {
            'cash': initial_capital,
            'commission': 0.0,
            'total': initial_capital
        }
    
    def update_timeindex(self, event) -> None:
        """Record positions and holdings at each timestamp."""
        self.all_positions.append({
            **self.current_positions,
            'datetime': event.timestamp
        })
        self.all_holdings.append({
            **self.current_holdings,
            'datetime': event.timestamp
        })
    
    def update_positions_from_fill(self, fill: FillEvent) -> None:
        """Adjust positions based on fill event."""
        fill_dir = 1 if fill.direction == 'BUY' else -1
        self.current_positions.setdefault(fill.symbol, 0)
        self.current_positions[fill.symbol] += fill_dir * fill.quantity
    
    def update_holdings_from_fill(self, fill: FillEvent) -> None:
        """Adjust cash and equity based on fill event."""
        fill_dir = 1 if fill.direction == 'BUY' else -1
        cost = fill_dir * fill.fill_cost
        
        self.current_holdings['cash'] -= cost + fill.commission
        self.current_holdings['commission'] += fill.commission
        self.current_holdings.setdefault(fill.symbol, 0.0)
        self.current_holdings[fill.symbol] += cost
        
        # Update total equity
        self.current_holdings['total'] = (
            self.current_holdings['cash'] + 
            sum(v for k, v in self.current_holdings.items() 
                if k not in ['cash', 'commission', 'total', 'datetime'])
        )
    
    def update_fill(self, event: FillEvent) -> None:
        """Handle fill event and update positions/holdings."""
        self.update_positions_from_fill(event)
        self.update_holdings_from_fill(event)
    
    def generate_order(self, signal: SignalEvent) -> None:
        """Convert signals to orders."""
        order = None
        symbol = signal.symbol
        direction = 'BUY' if signal.signal_type == 'LONG' else 'SELL'
        
        # Simple fixed quantity for now
        mkt_quantity = 100
        
        order = OrderEvent(
            timestamp=signal.timestamp,
            symbol=symbol,
            order_type='MKT',
            quantity=mkt_quantity,
            direction=direction,
            data=None
        )
        
        if order is not None:
            self.events.put(order)
    
    def get_holdings_curve(self) -> pd.DataFrame:
        """Return equity curve as DataFrame."""
        return pd.DataFrame(self.all_holdings)
    
    def get_positions(self) -> pd.DataFrame:
        """Get positions as DataFrame."""
        return pd.DataFrame(self.all_positions)

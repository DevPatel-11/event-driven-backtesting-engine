from queue import Queue
from datetime import datetime
from typing import Type, Dict, Tuple

from .market_data.data_handler import DataHandler
from .strategy.base_strategy import Strategy
from .portfolio.portfolio import Portfolio
from .execution.execution import ExecutionHandler
from .utils.events import EventType
from .utils.performance import PerformanceMetrics
import pandas as pd


class BacktestEngine:
    """Main backtesting engine that coordinates all components."""
    
    def __init__(
        self,
        csv_dir: str,
        symbol_list: list,
        initial_capital: float,
        start_date: datetime,
        data_handler_cls: Type[DataHandler],
        execution_handler_cls: Type[ExecutionHandler],
        portfolio_cls: Type[Portfolio],
        strategy_cls: Type[Strategy]
    ):
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.start_date = start_date
        
        self.events = Queue()
        
        # Initialize components
        self.data_handler = data_handler_cls(self.events, csv_dir, symbol_list)
        self.strategy = strategy_cls(self.events, self.data_handler)
        self.portfolio = portfolio_cls(self.events, start_date, initial_capital)
        self.execution_handler = execution_handler_cls(self.events, self.data_handler)
        
        # Track execution statistics
        self.signals = 0
        self.orders = 0
        self.fills = 0
    
    def _run_backtest(self) -> None:
        """Execute the main event loop."""
        while True:
            # Update market data
            if self.data_handler.continue_backtest:
                self.data_handler.update_bars()
            else:
                break
            
            # Process event queue
            while True:
                try:
                    event = self.events.get(False)
                except:
                    break
                else:
                    if event is not None:
                        if event.type == EventType.MARKET:
                            self.strategy.on_tick(event)
                            self.portfolio.update_timeindex(event)
                        
                        elif event.type == EventType.SIGNAL:
                            self.signals += 1
                            self.portfolio.generate_order(event)
                        
                        elif event.type == EventType.ORDER:
                            self.orders += 1
                            self.execution_handler.execute_order(event)
                        
                        elif event.type == EventType.FILL:
                            self.fills += 1
                            self.portfolio.update_fill(event)
    
    def run(self) -> Tuple[Dict[str, float], pd.DataFrame]:
        """Run backtest and return performance metrics."""
        self._run_backtest()
        
        # Calculate performance metrics
        equity_curve = self.portfolio.get_holdings_curve()
        metrics = PerformanceMetrics.calculate_metrics(equity_curve)
        
        # Add execution statistics
        metrics['signals'] = self.signals
        metrics['orders'] = self.orders
        metrics['fills'] = self.fills
        
        return metrics, equity_curve

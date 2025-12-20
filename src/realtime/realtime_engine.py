"""Real-time trading engine for live strategy execution."""
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from queue import Queue, Empty
from threading import Thread

logger = logging.getLogger(__name__)


class RealtimeEngine:
    """Real-time trading engine for live market execution."""
    
    def __init__(
        self,
        strategy,
        data_feed,
        execution_handler,
        portfolio
    ):
        """Initialize real-time trading engine.
        
        Args:
            strategy: Trading strategy instance
            data_feed: Real-time data feed (WebSocket)
            execution_handler: Order execution handler
            portfolio: Portfolio manager
        """
        self.strategy = strategy
        self.data_feed = data_feed
        self.execution_handler = execution_handler
        self.portfolio = portfolio
        
        self.event_queue = Queue()
        self.running = False
        self.event_thread: Optional[Thread] = None
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        self.ticks_processed = 0
        self.orders_generated = 0
    
    def start(self) -> None:
        """Start the real-time trading engine."""
        logger.info("Starting real-time trading engine...")
        self.running = True
        self.start_time = datetime.now()
        
        # Start event processing thread
        self.event_thread = Thread(target=self._process_events, daemon=True)
        self.event_thread.start()
        
        # Start data feed in asyncio event loop
        asyncio.run(self._run_data_feed())
    
    async def _run_data_feed(self) -> None:
        """Run the WebSocket data feed."""
        # Set data feed callback
        self.data_feed.on_tick = self._on_market_tick
        
        try:
            await self.data_feed.start()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.stop()
    
    def _on_market_tick(self, tick_data: Dict[str, Any]) -> None:
        """Handle incoming market tick.
        
        Args:
            tick_data: Market tick data
        """
        # Convert to market event and queue it
        market_event = {
            'type': 'MARKET',
            'data': tick_data
        }
        self.event_queue.put(market_event)
        self.ticks_processed += 1
    
    def _process_events(self) -> None:
        """Process events from the queue (runs in separate thread)."""
        logger.info("Event processing thread started")
        
        while self.running:
            try:
                # Get event from queue with timeout
                event = self.event_queue.get(timeout=1.0)
                
                if event['type'] == 'MARKET':
                    self._handle_market_event(event['data'])
                elif event['type'] == 'SIGNAL':
                    self._handle_signal_event(event['data'])
                elif event['type'] == 'ORDER':
                    self._handle_order_event(event['data'])
                elif event['type'] == 'FILL':
                    self._handle_fill_event(event['data'])
                    
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
        
        logger.info("Event processing thread stopped")
    
    def _handle_market_event(self, tick_data: Dict[str, Any]) -> None:
        """Handle market data event.
        
        Args:
            tick_data: Market tick data
        """
        try:
            # Update strategy with new market data
            self.strategy.on_tick(tick_data)
            
            # Generate trading signals
            signals = self.strategy.generate_signal(tick_data)
            
            if signals:
                for signal in signals:
                    self.event_queue.put({
                        'type': 'SIGNAL',
                        'data': signal
                    })
        except Exception as e:
            logger.error(f"Error handling market event: {e}")
    
    def _handle_signal_event(self, signal: Dict[str, Any]) -> None:
        """Handle trading signal event.
        
        Args:
            signal: Trading signal data
        """
        try:
            # Create order from signal
            order = self._create_order_from_signal(signal)
            
            if order:
                self.event_queue.put({
                    'type': 'ORDER',
                    'data': order
                })
                self.orders_generated += 1
        except Exception as e:
            logger.error(f"Error handling signal event: {e}")
    
    def _handle_order_event(self, order: Dict[str, Any]) -> None:
        """Handle order event.
        
        Args:
            order: Order data
        """
        try:
            # Execute order through execution handler
            fill = self.execution_handler.execute_order(order)
            
            if fill:
                self.event_queue.put({
                    'type': 'FILL',
                    'data': fill
                })
        except Exception as e:
            logger.error(f"Error handling order event: {e}")
    
    def _handle_fill_event(self, fill: Dict[str, Any]) -> None:
        """Handle fill event.
        
        Args:
            fill: Fill data
        """
        try:
            # Update portfolio with fill
            self.portfolio.update_fill(fill)
            
            logger.info(f"Fill executed: {fill['symbol']} {fill['side']} "
                       f"{fill['quantity']} @ {fill['price']}")
        except Exception as e:
            logger.error(f"Error handling fill event: {e}")
    
    def _create_order_from_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create order from trading signal.
        
        Args:
            signal: Trading signal
            
        Returns:
            Order dictionary or None
        """
        if signal.get('action') == 'BUY':
            return {
                'symbol': signal['symbol'],
                'side': 'BUY',
                'quantity': signal.get('quantity', 100),
                'order_type': 'MARKET',
                'timestamp': datetime.now()
            }
        elif signal.get('action') == 'SELL':
            return {
                'symbol': signal['symbol'],
                'side': 'SELL',
                'quantity': signal.get('quantity', 100),
                'order_type': 'MARKET',
                'timestamp': datetime.now()
            }
        return None
    
    async def stop(self) -> None:
        """Stop the real-time trading engine."""
        logger.info("Stopping real-time trading engine...")
        self.running = False
        
        # Stop data feed
        await self.data_feed.stop()
        
        # Wait for event thread to finish
        if self.event_thread and self.event_thread.is_alive():
            self.event_thread.join(timeout=5.0)
        
        # Log statistics
        runtime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        logger.info(f"Runtime: {runtime:.2f}s")
        logger.info(f"Ticks processed: {self.ticks_processed}")
        logger.info(f"Orders generated: {self.orders_generated}")
        logger.info(f"Final portfolio value: ${self.portfolio.current_holdings['total']:.2f}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        runtime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            'runtime_seconds': runtime,
            'ticks_processed': self.ticks_processed,
            'orders_generated': self.orders_generated,
            'ticks_per_second': self.ticks_processed / runtime if runtime > 0 else 0,
            'portfolio_value': self.portfolio.current_holdings['total'],
            'queue_size': self.event_queue.qsize()
        }

"""WebSocket data feed handler for real-time market data."""
import asyncio
import json
import logging
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
from queue import Queue
import websockets
from websockets.client import WebSocketClientProtocol

logger = logging.getLogger(__name__)


class WebSocketDataFeed:
    """WebSocket client for real-time market data streaming."""
    
    def __init__(
        self,
        url: str,
        symbols: List[str],
        on_tick: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        reconnect_interval: int = 5
    ):
        """Initialize WebSocket data feed.
        
        Args:
            url: WebSocket server URL
            symbols: List of trading symbols to subscribe
            on_tick: Callback for market data ticks
            on_error: Callback for error handling
            reconnect_interval: Seconds to wait before reconnection
        """
        self.url = url
        self.symbols = symbols
        self.on_tick = on_tick
        self.on_error = on_error
        self.reconnect_interval = reconnect_interval
        
        self.ws: Optional[WebSocketClientProtocol] = None
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.message_queue = Queue()
    
    async def connect(self) -> None:
        """Establish WebSocket connection."""
        try:
            self.ws = await websockets.connect(
                self.url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5
            )
            logger.info(f"Connected to WebSocket: {self.url}")
            await self.subscribe_symbols()
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            if self.on_error:
                self.on_error(e)
            raise
    
    async def subscribe_symbols(self) -> None:
        """Subscribe to market data for configured symbols."""
        if not self.ws:
            return
        
        subscribe_message = {
            'action': 'subscribe',
            'symbols': self.symbols,
            'data_type': 'trades'
        }
        
        await self.ws.send(json.dumps(subscribe_message))
        logger.info(f"Subscribed to symbols: {self.symbols}")
    
    async def listen(self) -> None:
        """Listen for incoming WebSocket messages."""
        while self.running and self.ws:
            try:
                message = await asyncio.wait_for(
                    self.ws.recv(),
                    timeout=30.0
                )
                await self.handle_message(message)
            except asyncio.TimeoutError:
                logger.warning("WebSocket receive timeout, sending ping...")
                if self.ws:
                    try:
                        await self.ws.ping()
                    except Exception as e:
                        logger.error(f"Ping failed: {e}")
                        break
            except websockets.exceptions.ConnectionClosed as e:
                logger.error(f"Connection closed: {e}")
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                if self.on_error:
                    self.on_error(e)
                break
    
    async def handle_message(self, message: str) -> None:
        """Process incoming WebSocket message.
        
        Args:
            message: Raw WebSocket message
        """
        try:
            data = json.loads(message)
            
            # Handle different message types
            if 'type' in data:
                if data['type'] == 'trade':
                    await self.handle_trade(data)
                elif data['type'] == 'quote':
                    await self.handle_quote(data)
                elif data['type'] == 'error':
                    await self.handle_error(data)
                else:
                    logger.warning(f"Unknown message type: {data['type']}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            if self.on_error:
                self.on_error(e)
    
    async def handle_trade(self, data: Dict[str, Any]) -> None:
        """Handle trade data message.
        
        Args:
            data: Trade data dictionary
        """
        tick_data = {
            'symbol': data.get('symbol'),
            'price': float(data.get('price', 0)),
            'size': float(data.get('size', 0)),
            'timestamp': datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            'side': data.get('side', 'unknown')
        }
        
        if self.on_tick:
            self.on_tick(tick_data)
        
        self.message_queue.put(tick_data)
    
    async def handle_quote(self, data: Dict[str, Any]) -> None:
        """Handle quote data message.
        
        Args:
            data: Quote data dictionary
        """
        quote_data = {
            'symbol': data.get('symbol'),
            'bid': float(data.get('bid', 0)),
            'ask': float(data.get('ask', 0)),
            'bid_size': float(data.get('bid_size', 0)),
            'ask_size': float(data.get('ask_size', 0)),
            'timestamp': datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
        }
        
        if self.on_tick:
            self.on_tick(quote_data)
    
    async def handle_error(self, data: Dict[str, Any]) -> None:
        """Handle error message from server.
        
        Args:
            data: Error data dictionary
        """
        error_msg = data.get('message', 'Unknown error')
        logger.error(f"Server error: {error_msg}")
        if self.on_error:
            self.on_error(Exception(error_msg))
    
    async def start(self) -> None:
        """Start WebSocket data feed with auto-reconnection."""
        self.running = True
        
        while self.running:
            try:
                await self.connect()
                await self.listen()
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            
            if self.running:
                logger.info(f"Reconnecting in {self.reconnect_interval} seconds...")
                await asyncio.sleep(self.reconnect_interval)
    
    async def stop(self) -> None:
        """Stop WebSocket data feed gracefully."""
        logger.info("Stopping WebSocket data feed...")
        self.running = False
        
        if self.ws:
            await self.ws.close()
            self.ws = None
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("WebSocket data feed stopped")
    
    def get_queued_messages(self) -> List[Dict[str, Any]]:
        """Get all queued messages.
        
        Returns:
            List of queued market data messages
        """
        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())
        return messages

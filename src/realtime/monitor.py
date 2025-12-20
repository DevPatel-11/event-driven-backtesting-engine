"""Real-time monitoring and metrics collection."""
import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
import threading

logger = logging.getLogger(__name__)


class RealtimeMonitor:
    """Monitor real-time trading performance and system metrics."""
    
    def __init__(self, window_size: int = 100):
        """Initialize real-time monitor.
        
        Args:
            window_size: Size of rolling window for metrics
        """
        self.window_size = window_size
        self.metrics = {
            'latency': deque(maxlen=window_size),
            'ticks_per_second': deque(maxlen=window_size),
            'order_fill_time': deque(maxlen=window_size),
            'pnl_updates': deque(maxlen=window_size)
        }
        
        self.start_time = datetime.now()
        self.last_tick_time = None
        self.tick_counter = 0
        self.order_counter = 0
        self.fill_counter = 0
        
        self._lock = threading.Lock()
    
    def record_tick(self, tick_data: Dict[str, Any]) -> None:
        """Record market tick for latency measurement.
        
        Args:
            tick_data: Market tick data with timestamp
        """
        with self._lock:
            now = datetime.now()
            
            # Calculate tick-to-processing latency
            if 'timestamp' in tick_data:
                tick_time = tick_data['timestamp']
                if isinstance(tick_time, str):
                    tick_time = datetime.fromisoformat(tick_time)
                latency_ms = (now - tick_time).total_seconds() * 1000
                self.metrics['latency'].append(latency_ms)
            
            # Calculate ticks per second
            if self.last_tick_time:
                interval = (now - self.last_tick_time).total_seconds()
                if interval > 0:
                    tps = 1.0 / interval
                    self.metrics['ticks_per_second'].append(tps)
            
            self.last_tick_time = now
            self.tick_counter += 1
    
    def record_order(self, order_data: Dict[str, Any]) -> None:
        """Record order placement.
        
        Args:
            order_data: Order data
        """
        with self._lock:
            self.order_counter += 1
            # Store order timestamp for fill time calculation
            if 'timestamp' in order_data:
                order_data['_monitor_timestamp'] = datetime.now()
    
    def record_fill(self, fill_data: Dict[str, Any], order_data: Dict[str, Any] = None) -> None:
        """Record order fill for execution time measurement.
        
        Args:
            fill_data: Fill data
            order_data: Original order data (optional)
        """
        with self._lock:
            self.fill_counter += 1
            
            # Calculate order-to-fill time
            if order_data and '_monitor_timestamp' in order_data:
                fill_time_ms = (datetime.now() - order_data['_monitor_timestamp']).total_seconds() * 1000
                self.metrics['order_fill_time'].append(fill_time_ms)
    
    def record_pnl(self, pnl: float) -> None:
        """Record PnL update.
        
        Args:
            pnl: Profit and loss value
        """
        with self._lock:
            self.metrics['pnl_updates'].append({
                'timestamp': datetime.now(),
                'pnl': pnl
            })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        with self._lock:
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            stats = {
                'uptime_seconds': uptime,
                'total_ticks': self.tick_counter,
                'total_orders': self.order_counter,
                'total_fills': self.fill_counter,
                'avg_ticks_per_second': self.tick_counter / uptime if uptime > 0 else 0
            }
            
            # Latency statistics
            if self.metrics['latency']:
                latencies = list(self.metrics['latency'])
                stats['latency'] = {
                    'avg_ms': sum(latencies) / len(latencies),
                    'min_ms': min(latencies),
                    'max_ms': max(latencies),
                    'p50_ms': self._percentile(latencies, 50),
                    'p95_ms': self._percentile(latencies, 95),
                    'p99_ms': self._percentile(latencies, 99)
                }
            
            # Order fill time statistics
            if self.metrics['order_fill_time']:
                fill_times = list(self.metrics['order_fill_time'])
                stats['order_fill_time'] = {
                    'avg_ms': sum(fill_times) / len(fill_times),
                    'min_ms': min(fill_times),
                    'max_ms': max(fill_times)
                }
            
            # Recent PnL
            if self.metrics['pnl_updates']:
                recent_pnl = list(self.metrics['pnl_updates'])[-10:]
                stats['recent_pnl'] = [p['pnl'] for p in recent_pnl]
                stats['latest_pnl'] = recent_pnl[-1]['pnl'] if recent_pnl else 0
            
            return stats
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value.
        
        Args:
            data: List of values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int((percentile / 100.0) * len(sorted_data))
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        return sorted_data[index]
    
    def print_stats(self) -> None:
        """Print current statistics to logger."""
        stats = self.get_statistics()
        
        logger.info("=" * 50)
        logger.info("REAL-TIME MONITORING STATS")
        logger.info("=" * 50)
        logger.info(f"Uptime: {stats['uptime_seconds']:.2f}s")
        logger.info(f"Total Ticks: {stats['total_ticks']}")
        logger.info(f"Total Orders: {stats['total_orders']}")
        logger.info(f"Total Fills: {stats['total_fills']}")
        logger.info(f"Avg Ticks/Second: {stats['avg_ticks_per_second']:.2f}")
        
        if 'latency' in stats:
            lat = stats['latency']
            logger.info(f"\nLatency Stats:")
            logger.info(f"  Average: {lat['avg_ms']:.2f}ms")
            logger.info(f"  P50: {lat['p50_ms']:.2f}ms")
            logger.info(f"  P95: {lat['p95_ms']:.2f}ms")
            logger.info(f"  P99: {lat['p99_ms']:.2f}ms")
            logger.info(f"  Min/Max: {lat['min_ms']:.2f}ms / {lat['max_ms']:.2f}ms")
        
        if 'order_fill_time' in stats:
            fill = stats['order_fill_time']
            logger.info(f"\nOrder Fill Time:")
            logger.info(f"  Average: {fill['avg_ms']:.2f}ms")
            logger.info(f"  Min/Max: {fill['min_ms']:.2f}ms / {fill['max_ms']:.2f}ms")
        
        if 'latest_pnl' in stats:
            logger.info(f"\nLatest PnL: ${stats['latest_pnl']:.2f}")
        
        logger.info("=" * 50)


class PerformanceAlert:
    """Alert system for performance issues."""
    
    def __init__(
        self,
        latency_threshold_ms: float = 1000.0,
        fill_time_threshold_ms: float = 5000.0
    ):
        """Initialize performance alert system.
        
        Args:
            latency_threshold_ms: Alert threshold for tick latency
            fill_time_threshold_ms: Alert threshold for fill time
        """
        self.latency_threshold = latency_threshold_ms
        self.fill_time_threshold = fill_time_threshold_ms
        self.alerts: List[Dict[str, Any]] = []
    
    def check_latency(self, latency_ms: float) -> None:
        """Check if latency exceeds threshold.
        
        Args:
            latency_ms: Current latency in milliseconds
        """
        if latency_ms > self.latency_threshold:
            alert = {
                'type': 'HIGH_LATENCY',
                'timestamp': datetime.now(),
                'value': latency_ms,
                'threshold': self.latency_threshold
            }
            self.alerts.append(alert)
            logger.warning(f"HIGH LATENCY ALERT: {latency_ms:.2f}ms (threshold: {self.latency_threshold}ms)")
    
    def check_fill_time(self, fill_time_ms: float) -> None:
        """Check if fill time exceeds threshold.
        
        Args:
            fill_time_ms: Order fill time in milliseconds
        """
        if fill_time_ms > self.fill_time_threshold:
            alert = {
                'type': 'SLOW_FILL',
                'timestamp': datetime.now(),
                'value': fill_time_ms,
                'threshold': self.fill_time_threshold
            }
            self.alerts.append(alert)
            logger.warning(f"SLOW FILL ALERT: {fill_time_ms:.2f}ms (threshold: {self.fill_time_threshold}ms)")
    
    def get_recent_alerts(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get alerts from recent time window.
        
        Args:
            minutes: Time window in minutes
            
        Returns:
            List of recent alerts
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [a for a in self.alerts if a['timestamp'] >= cutoff]

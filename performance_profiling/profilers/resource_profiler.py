"""Resource profiling for CPU and memory usage."""

import psutil
import time
import threading
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ResourceSnapshot:
    """Single snapshot of resource usage."""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float


class ResourceProfiler:
    """Profile CPU and memory usage during backtest execution."""
    
    def __init__(self, sample_interval: float = 0.1):
        """Initialize resource profiler.
        
        Args:
            sample_interval: Time between samples in seconds
        """
        self.sample_interval = sample_interval
        self.snapshots: List[ResourceSnapshot] = []
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self.process = psutil.Process()
        
    def start(self):
        """Start monitoring resources."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
    def stop(self):
        """Stop monitoring resources."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self._monitoring:
            snapshot = ResourceSnapshot(
                timestamp=time.time(),
                cpu_percent=self.process.cpu_percent(interval=None),
                memory_mb=self.process.memory_info().rss / (1024 * 1024),
                memory_percent=self.process.memory_percent()
            )
            self.snapshots.append(snapshot)
            time.sleep(self.sample_interval)
    
    def get_stats(self) -> Dict:
        """Get summary statistics."""
        if not self.snapshots:
            return {}
        
        cpu_values = [s.cpu_percent for s in self.snapshots]
        memory_values = [s.memory_mb for s in self.snapshots]
        
        return {
            'cpu_percent': {
                'mean': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory_mb': {
                'mean': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values),
                'peak': max(memory_values)
            },
            'num_samples': len(self.snapshots)
        }
    
    def reset(self):
        """Clear collected snapshots."""
        self.snapshots.clear()

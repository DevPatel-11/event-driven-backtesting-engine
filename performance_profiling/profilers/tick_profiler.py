"""Per-tick processing time profiler."""

import time
import statistics
from typing import List, Dict
from collections import defaultdict


class TickProfiler:
    """Profile per-tick processing time."""
    
    def __init__(self):
        self.tick_times: List[float] = []
        self.component_times: Dict[str, List[float]] = defaultdict(list)
        self._start_time: float = 0
        self._component_start: float = 0
        self.total_ticks: int = 0
        
    def start_tick(self):
        """Start timing a tick."""
        self._start_time = time.perf_counter()
        
    def end_tick(self):
        """End timing a tick."""
        elapsed = time.perf_counter() - self._start_time
        self.tick_times.append(elapsed)
        self.total_ticks += 1
        
    def start_component(self, name: str):
        """Start timing a component."""
        self._component_start = time.perf_counter()
        
    def end_component(self, name: str):
        """End timing a component."""
        elapsed = time.perf_counter() - self._component_start
        self.component_times[name].append(elapsed)
    
    def get_stats(self) -> Dict:
        """Get timing statistics."""
        if not self.tick_times:
            return {}
        
        # Per-tick statistics
        tick_stats = {
            'mean_us': statistics.mean(self.tick_times) * 1e6,
            'median_us': statistics.median(self.tick_times) * 1e6,
            'min_us': min(self.tick_times) * 1e6,
            'max_us': max(self.tick_times) * 1e6,
            'stddev_us': statistics.stdev(self.tick_times) * 1e6 if len(self.tick_times) > 1 else 0,
            'total_ticks': self.total_ticks,
            'ticks_per_second': self.total_ticks / sum(self.tick_times) if sum(self.tick_times) > 0 else 0
        }
        
        # Component-level statistics
        component_stats = {}
        for name, times in self.component_times.items():
            component_stats[name] = {
                'mean_us': statistics.mean(times) * 1e6,
                'total_calls': len(times),
                'total_time_ms': sum(times) * 1000
            }
        
        return {
            'tick_stats': tick_stats,
            'component_stats': component_stats
        }
    
    def get_percentiles(self, percentiles: List[int] = [50, 90, 95, 99]) -> Dict:
        """Get percentile statistics."""
        if not self.tick_times:
            return {}
        
        sorted_times = sorted(self.tick_times)
        n = len(sorted_times)
        
        result = {}
        for p in percentiles:
            idx = int((p / 100.0) * n)
            if idx >= n:
                idx = n - 1
            result[f'p{p}_us'] = sorted_times[idx] * 1e6
        
        return result
    
    def reset(self):
        """Clear all timing data."""
        self.tick_times.clear()
        self.component_times.clear()
        self.total_ticks = 0

"""Centralized metrics collection."""

import json
import time
from typing import Dict, Any
from .resource_profiler import ResourceProfiler
from .tick_profiler import TickProfiler


class MetricsCollector:
    """Centralized collector for all performance metrics."""
    
    def __init__(self, sample_interval: float = 0.1):
        self.resource_profiler = ResourceProfiler(sample_interval=sample_interval)
        self.tick_profiler = TickProfiler()
        self.start_time: float = 0
        self.end_time: float = 0
        self.benchmark_name: str = ""
        
    def start_profiling(self, benchmark_name: str = "backtest"):
        """Start all profilers."""
        self.benchmark_name = benchmark_name
        self.start_time = time.time()
        self.resource_profiler.start()
        
    def stop_profiling(self):
        """Stop all profilers."""
        self.end_time = time.time()
        self.resource_profiler.stop()
        
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        total_time = self.end_time - self.start_time if self.end_time > 0 else 0
        
        return {
            'benchmark_name': self.benchmark_name,
            'total_time_seconds': total_time,
            'resource_usage': self.resource_profiler.get_stats(),
            'tick_performance': self.tick_profiler.get_stats(),
            'tick_percentiles': self.tick_profiler.get_percentiles(),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def save_metrics(self, output_file: str):
        """Save metrics to JSON file."""
        metrics = self.get_all_metrics()
        with open(output_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def print_summary(self):
        """Print summary of metrics."""
        metrics = self.get_all_metrics()
        
        print("\n" + "="*80)
        print(f"Performance Metrics: {metrics['benchmark_name']}")
        print("="*80)
        
        # Time
        print(f"\nTotal Time: {metrics['total_time_seconds']:.2f} seconds")
        
        # Tick Performance
        if 'tick_stats' in metrics['tick_performance']:
            tick_stats = metrics['tick_performance']['tick_stats']
            print(f"\nTick Processing:")
            print(f"  Total Ticks: {tick_stats['total_ticks']:,}")
            print(f"  Ticks/second: {tick_stats['ticks_per_second']:,.0f}")
            print(f"  Mean Time: {tick_stats['mean_us']:.2f} µs")
            print(f"  Median Time: {tick_stats['median_us']:.2f} µs")
            print(f"  Min/Max: {tick_stats['min_us']:.2f} / {tick_stats['max_us']:.2f} µs")
        
        # Percentiles
        if metrics['tick_percentiles']:
            print(f"\nPercentiles:")
            for key, value in sorted(metrics['tick_percentiles'].items()):
                print(f"  {key}: {value:.2f} µs")
        
        # Resource Usage
        if 'cpu_percent' in metrics['resource_usage']:
            cpu = metrics['resource_usage']['cpu_percent']
            mem = metrics['resource_usage']['memory_mb']
            print(f"\nResource Usage:")
            print(f"  CPU: {cpu['mean']:.1f}% (max: {cpu['max']:.1f}%)")
            print(f"  Memory: {mem['mean']:.1f} MB (peak: {mem['peak']:.1f} MB)")
        
        print("="*80 + "\n")
    
    def reset(self):
        """Reset all profilers."""
        self.resource_profiler.reset()
        self.tick_profiler.reset()
        self.start_time = 0
        self.end_time = 0

#!/usr/bin/env python3
"""Scalability benchmark: Test with millions of ticks."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import random
import time
from performance_profiling.profilers import MetricsCollector

def simulate_tick_processing(num_ticks: int, metrics: MetricsCollector):
    """Simulate backtest processing of ticks."""
    for i in range(num_ticks):
        metrics.tick_profiler.start_tick()
        
        # Simulate tick processing work
        _ = sum(range(100))  # Minimal work
        
        # Simulate occasional heavier operations
        if i % 1000 == 0:
            _ = [x**2 for x in range(50)]
        
        metrics.tick_profiler.end_tick()

def run_benchmark(tick_counts: list = [10000, 100000, 1000000]):
    """Run scalability benchmarks with different tick counts."""
    results = []
    
    print("\n" + "="*80)
    print("SCALABILITY BENCHMARK")
    print("="*80)
    
    for num_ticks in tick_counts:
        print(f"\nTesting with {num_ticks:,} ticks...")
        
        metrics = MetricsCollector(sample_interval=0.5)
        metrics.start_profiling(f"scalability_{num_ticks}")
        
        simulate_tick_processing(num_ticks, metrics)
        
        metrics.stop_profiling()
        metrics.print_summary()
        
        # Save results
        output_file = f"performance_profiling/reports/scalability_{num_ticks}.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        metrics.save_metrics(output_file)
        
        all_metrics = metrics.get_all_metrics()
        results.append({
            'ticks': num_ticks,
            'total_time': all_metrics['total_time_seconds'],
            'ticks_per_sec': all_metrics['tick_performance']['tick_stats']['ticks_per_second'] if 'tick_stats' in all_metrics['tick_performance'] else 0
        })
    
    # Print comparison
    print("\n" + "="*80)
    print("SCALABILITY COMPARISON")
    print("="*80)
    print(f"{'Ticks':<15} {'Total Time':<15} {'Ticks/sec':<15} {'Scaling'}")
    print("-"*80)
    
    base_tps = results[0]['ticks_per_sec'] if results else 0
    for r in results:
        scaling = f"{(r['ticks_per_sec']/base_tps)*100:.1f}%" if base_tps > 0 else "N/A"
        print(f"{r['ticks']:>14,} {r['total_time']:>14.2f}s {r['ticks_per_sec']:>14,.0f} {scaling:>10}")
    
    print("="*80 + "\n")

if __name__ == '__main__':
    run_benchmark()

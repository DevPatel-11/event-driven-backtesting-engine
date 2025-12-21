#!/usr/bin/env python3
"""Generate performance graphs from metrics."""

import json
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

def load_metrics(filename):
    """Load metrics from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def generate_scalability_graph(reports_dir='performance_profiling/reports'):
    """Generate scalability comparison graph."""
    # Load all scalability reports
    metrics_files = [f for f in os.listdir(reports_dir) if f.startswith('scalability_') and f.endswith('.json')]
    
    data = []
    for filename in sorted(metrics_files):
        filepath = os.path.join(reports_dir, filename)
        metrics = load_metrics(filepath)
        
        if 'tick_stats' in metrics.get('tick_performance', {}):
            tick_stats = metrics['tick_performance']['tick_stats']
            data.append({
                'ticks': tick_stats['total_ticks'],
                'ticks_per_sec': tick_stats['ticks_per_second'],
                'total_time': metrics['total_time_seconds'],
                'avg_latency_us': tick_stats['mean_us']
            })
    
    if not data:
        print("No metrics data found.")
        return
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Performance Scalability Metrics', fontsize=16, fontweight='bold')
    
    ticks = [d['ticks'] for d in data]
    
    # 1. Throughput (ticks/sec)
    ax1.bar(range(len(data)), [d['ticks_per_sec'] for d in data], color='#2E86AB')
    ax1.set_xticks(range(len(data)))
    ax1.set_xticklabels([f"{t/1000:.0f}K" for t in ticks])
    ax1.set_xlabel('Number of Ticks')
    ax1.set_ylabel('Ticks/Second')
    ax1.set_title('Throughput (Higher is Better)')
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Total Time
    ax2.plot(range(len(data)), [d['total_time'] for d in data], marker='o', color='#A23B72', linewidth=2)
    ax2.set_xticks(range(len(data)))
    ax2.set_xticklabels([f"{t/1000:.0f}K" for t in ticks])
    ax2.set_xlabel('Number of Ticks')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_title('Total Execution Time')
    ax2.grid(alpha=0.3)
    
    # 3. Average Latency
    ax3.bar(range(len(data)), [d['avg_latency_us'] for d in data], color='#F18F01')
    ax3.set_xticks(range(len(data)))
    ax3.set_xticklabels([f"{t/1000:.0f}K" for t in ticks])
    ax3.set_xlabel('Number of Ticks')
    ax3.set_ylabel('Latency (µs)')
    ax3.set_title('Average Per-Tick Latency (Lower is Better)')
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Efficiency (ticks/sec normalized)
    base_tps = data[0]['ticks_per_sec']
    efficiency = [(d['ticks_per_sec']/base_tps)*100 for d in data]
    ax4.plot(range(len(data)), efficiency, marker='s', color='#06A77D', linewidth=2)
    ax4.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='Baseline')
    ax4.set_xticks(range(len(data)))
    ax4.set_xticklabels([f"{t/1000:.0f}K" for t in ticks])
    ax4.set_xlabel('Number of Ticks')
    ax4.set_ylabel('Efficiency (%)')
    ax4.set_title('Scaling Efficiency vs Baseline')
    ax4.legend()
    ax4.grid(alpha=0.3)
    
    plt.tight_layout()
    
    # Save
    output_path = 'performance_profiling/reports/scalability_metrics.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph saved to: {output_path}")
    plt.close()

if __name__ == '__main__':
    generate_scalability_graph()

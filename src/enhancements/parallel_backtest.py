"""Support for parallel backtest execution."""
import concurrent.futures
from typing import List, Dict, Any, Callable
import pandas as pd
from dataclasses import dataclass


@dataclass
class BacktestConfig:
    """Configuration for a single backtest run."""
    strategy_params: Dict[str, Any]
    data_file: str
    initial_capital: float = 100000.0
    commission: float = 0.001
    slippage: float = 0.0005
    

class ParallelBacktestRunner:
    """
    Runner for executing multiple backtests in parallel.
    
    This class enables parameter optimization and strategy comparison
    by running multiple backtest configurations concurrently.
    """
    
    def __init__(self, max_workers: int = None):
        """
        Initialize parallel backtest runner.
        
        Args:
            max_workers: Maximum number of parallel workers (default: CPU count)
        """
        self.max_workers = max_workers
        self.results = []
    
    def run_single_backtest(self, config: BacktestConfig, 
                           backtest_fn: Callable) -> Dict[str, Any]:
        """
        Run a single backtest with given configuration.
        
        Args:
            config: Backtest configuration
            backtest_fn: Function that runs the backtest
            
        Returns:
            Dictionary of results
        """
        try:
            result = backtest_fn(config)
            result['config'] = config
            result['success'] = True
            return result
        except Exception as e:
            return {
                'config': config,
                'success': False,
                'error': str(e)
            }
    
    def run_parallel(self, configs: List[BacktestConfig],
                    backtest_fn: Callable) -> List[Dict[str, Any]]:
        """
        Run multiple backtests in parallel.
        
        Args:
            configs: List of backtest configurations
            backtest_fn: Function that runs a backtest
            
        Returns:
            List of results dictionaries
        """
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.run_single_backtest, config, backtest_fn)
                      for config in configs]
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({'success': False, 'error': str(e)})
        
        self.results = results
        return results
    
    def get_best_result(self, metric: str = 'sharpe_ratio',
                       maximize: bool = True) -> Dict[str, Any]:
        """
        Get best performing configuration.
        
        Args:
            metric: Performance metric to optimize
            maximize: Whether to maximize (True) or minimize (False)
            
        Returns:
            Best result dictionary
        """
        successful_results = [r for r in self.results if r.get('success', False)]
        
        if not successful_results:
            return None
        
        if maximize:
            return max(successful_results, key=lambda x: x.get(metric, float('-inf')))
        else:
            return min(successful_results, key=lambda x: x.get(metric, float('inf')))
    
    def results_to_dataframe(self) -> pd.DataFrame:
        """
        Convert results to pandas DataFrame for analysis.
        
        Returns:
            DataFrame of results
        """
        data = []
        for result in self.results:
            if result.get('success', False):
                row = {**result}
                # Flatten config
                if 'config' in row:
                    config = row.pop('config')
                    for k, v in config.strategy_params.items():
                        row[f'param_{k}'] = v
                data.append(row)
        
        return pd.DataFrame(data)

"""Realistic execution simulator with latency models."""

import random
import uuid
from typing import Dict, Any
from src.interfaces.execution_interface import IExecutionSimulator, ExecutionResult, LatencyModel
from src.interfaces.strategy_interface import Signal

class RealisticExecutionSimulator(IExecutionSimulator):
    """Execution simulator with configurable latency and slippage."""
    
    def __init__(self, latency_model: LatencyModel = LatencyModel.CONSTANT,
                 latency_params: Dict[str, float] = None,
                 slippage_bps: float = 2.0):
        self.latency_model = latency_model
        self.latency_params = latency_params or {'constant_ms': 5.0}
        self.slippage_bps = slippage_bps
    
    def execute_order(self, signal: Signal, market_price: float, timestamp: float) -> ExecutionResult:
        latency_ms = self._calculate_latency()
        slippage = self._calculate_slippage(market_price)
        filled_price = market_price + slippage
        return ExecutionResult(
            order_id=str(uuid.uuid4()),
            filled_price=filled_price,
            filled_quantity=signal.quantity,
            execution_time=timestamp + (latency_ms / 1000.0),
            latency_ms=latency_ms,
            slippage=slippage,
            commission=self._calculate_commission(signal.quantity, filled_price)
        )
    
    def _calculate_latency(self) -> float:
        if self.latency_model == LatencyModel.ZERO:
            return 0.0
        elif self.latency_model == LatencyModel.CONSTANT:
            return self.latency_params.get('constant_ms', 5.0)
        elif self.latency_model == LatencyModel.NORMAL:
            mean = self.latency_params.get('mean_ms', 5.0)
            std = self.latency_params.get('std_ms', 1.0)
            return max(0, random.gauss(mean, std))
        elif self.latency_model == LatencyModel.REALISTIC_HFT:
            return max(0.1, random.lognormvariate(1.0, 0.5))
        return 0.0
    
    def _calculate_slippage(self, price: float) -> float:
        return price * (self.slippage_bps / 10000.0) * random.uniform(0.5, 1.5)
    
    def _calculate_commission(self, quantity: float, price: float) -> float:
        return quantity * price * 0.0001
    
    def set_latency_model(self, model: LatencyModel, params: Dict[str, float]) -> None:
        self.latency_model = model
        self.latency_params = params

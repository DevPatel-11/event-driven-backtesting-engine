"""Execution simulator interface with latency models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum
import random

class LatencyModel(Enum):
    ZERO = "ZERO"
    CONSTANT = "CONSTANT"
    NORMAL = "NORMAL"
    REALISTIC_HFT = "REALISTIC_HFT"

@dataclass
class ExecutionResult:
    order_id: str
    filled_price: float
    filled_quantity: float
    execution_time: float
    latency_ms: float
    slippage: float = 0.0
    commission: float = 0.0
    metadata: Dict[str, Any] = None

class IExecutionSimulator(ABC):
    """Execution simulator with realistic latency and slippage models."""
    
    @abstractmethod
    def execute_order(self, signal: Any, market_price: float, timestamp: float) -> ExecutionResult:
        """Simulate order execution.
        
        Args:
            signal: Trading signal
            market_price: Current market price
            timestamp: Execution timestamp
            
        Returns:
            ExecutionResult with fill details
        """
        pass
    
    @abstractmethod
    def set_latency_model(self, model: LatencyModel, params: Dict[str, float]) -> None:
        """Configure latency model."""
        pass

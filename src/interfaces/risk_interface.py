"""Risk management interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

class RiskStatus(Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WARNING = "WARNING"

@dataclass
class RiskCheckResult:
    status: RiskStatus
    reason: str = ""
    max_allowed_quantity: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class IRiskManager(ABC):
    """Risk Manager interface for pre-trade risk checks."""
    
    @abstractmethod
    def check_order(self, signal: Any, current_position: Dict[str, float]) -> RiskCheckResult:
        """Check if order passes risk checks.
        
        Args:
            signal: Trading signal to validate
            current_position: Current portfolio positions
            
        Returns:
            RiskCheckResult with approval/rejection
        """
        pass
    
    @abstractmethod
    def update_limits(self, limits: Dict[str, Any]) -> None:
        """Update risk limits dynamically."""
        pass

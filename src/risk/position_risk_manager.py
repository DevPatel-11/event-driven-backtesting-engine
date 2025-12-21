"""Position-based risk management implementation."""

from typing import Dict, Any
from src.interfaces.risk_interface import IRiskManager, RiskCheckResult, RiskStatus
from src.interfaces.strategy_interface import Signal, SignalType


class PositionRiskManager(IRiskManager):
    """Risk manager enforcing position limits and exposure constraints."""
    
    def __init__(self, max_position_size: float = 1000.0,
                 max_portfolio_exposure: float = 100000.0,
                 max_concentration: float = 0.25):
        self.max_position_size = max_position_size
        self.max_portfolio_exposure = max_portfolio_exposure
        self.max_concentration = max_concentration
        
    def check_order(self, signal: Signal, current_position: Dict[str, float]) -> RiskCheckResult:
        """Check order against position limits."""
        # Check position size limit
        current_pos = current_position.get(signal.symbol, 0.0)
        new_position = self._calculate_new_position(signal, current_pos)
        
        if abs(new_position) > self.max_position_size:
            return RiskCheckResult(
                status=RiskStatus.REJECTED,
                reason=f"Position size {abs(new_position)} exceeds limit {self.max_position_size}",
                max_allowed_quantity=self.max_position_size - abs(current_pos)
            )
        
        # Check portfolio exposure
        total_exposure = sum(abs(p * signal.price or 0) for p in current_position.values())
        if total_exposure > self.max_portfolio_exposure:
            return RiskCheckResult(
                status=RiskStatus.REJECTED,
                reason=f"Portfolio exposure {total_exposure} exceeds limit {self.max_portfolio_exposure}"
            )
        
        # Check concentration (single position as % of portfolio)
        if total_exposure > 0:
            concentration = abs(new_position * (signal.price or 0)) / total_exposure
            if concentration > self.max_concentration:
                return RiskCheckResult(
                    status=RiskStatus.WARNING,
                    reason=f"Concentration {concentration:.1%} exceeds {self.max_concentration:.1%}"
                )
        
        return RiskCheckResult(status=RiskStatus.APPROVED, reason="All checks passed")
    
    def _calculate_new_position(self, signal: Signal, current_position: float) -> float:
        """Calculate new position after signal execution."""
        if signal.signal_type == SignalType.BUY:
            return current_position + signal.quantity
        elif signal.signal_type == SignalType.SELL:
            return current_position - signal.quantity
        elif signal.signal_type == SignalType.CLOSE_LONG:
            return 0.0
        elif signal.signal_type == SignalType.CLOSE_SHORT:
            return 0.0
        return current_position
    
    def update_limits(self, limits: Dict[str, Any]) -> None:
        """Dynamically update risk limits."""
        if 'max_position_size' in limits:
            self.max_position_size = limits['max_position_size']
        if 'max_portfolio_exposure' in limits:
            self.max_portfolio_exposure = limits['max_portfolio_exposure']
        if 'max_concentration' in limits:
            self.max_concentration = limits['max_concentration']

"""Advanced slippage models for realistic order execution simulation."""
from abc import ABC, abstractmethod
import numpy as np
from typing import Optional


class SlippageModel(ABC):
    """
    Abstract base class for slippage models.
    
    Slippage represents the difference between the expected execution price
    and the actual execution price.
    """
    
    @abstractmethod
    def calculate_slippage(self, price: float, quantity: int, 
                          volume: Optional[float] = None) -> float:
        """
        Calculate slippage for an order.
        
        Args:
            price: Expected execution price
            quantity: Order quantity (absolute value)
            volume: Market volume (if applicable)
            
        Returns:
            Slippage amount (absolute value)
        """
        pass


class FixedSlippage(SlippageModel):
    """
    Fixed slippage model - constant percentage slip.
    
    Simple model where slippage is a fixed percentage of the order price.
    Suitable for liquid markets with consistent execution costs.
    """
    
    def __init__(self, slippage_pct: float = 0.0005):
        """
        Initialize fixed slippage model.
        
        Args:
            slippage_pct: Slippage as decimal (e.g., 0.0005 for 0.05%)
        """
        self.slippage_pct = slippage_pct
    
    def calculate_slippage(self, price: float, quantity: int, 
                          volume: Optional[float] = None) -> float:
        """Calculate fixed slippage."""
        return price * self.slippage_pct


class VolumeBasedSlippage(SlippageModel):
    """
    Volume-based slippage model.
    
    Slippage increases as order size grows relative to market volume.
    More realistic for modeling market impact in varying liquidity conditions.
    """
    
    def __init__(self, base_slippage: float = 0.0001, 
                 impact_coefficient: float = 0.1):
        """
        Initialize volume-based slippage model.
        
        Args:
            base_slippage: Base slippage as decimal
            impact_coefficient: Market impact coefficient
        """
        self.base_slippage = base_slippage
        self.impact_coefficient = impact_coefficient
    
    def calculate_slippage(self, price: float, quantity: int, 
                          volume: Optional[float] = None) -> float:
        """
        Calculate volume-based slippage.
        
        Slippage = base + impact_coef * (quantity / volume)
        """
        base = price * self.base_slippage
        
        if volume is None or volume == 0:
            # If no volume data, use base slippage
            return base
        
        # Calculate market impact
        volume_ratio = abs(quantity) / volume
        impact = price * self.impact_coefficient * volume_ratio
        
        return base + impact


class SquareRootSlippage(SlippageModel):
    """
    Square-root market impact model.
    
    Based on empirical research showing market impact grows with
    the square root of order size. Common in institutional trading models.
    
    Reference: Almgren, Robert, et al. "Direct estimation of equity market impact."
    """
    
    def __init__(self, volatility: float = 0.02, 
                 participation_rate: float = 0.1,
                 permanent_impact: float = 0.1,
                 temporary_impact: float = 0.01):
        """
        Initialize square-root slippage model.
        
        Args:
            volatility: Daily volatility (as decimal)
            participation_rate: Order size as fraction of daily volume
            permanent_impact: Permanent impact coefficient
            temporary_impact: Temporary impact coefficient
        """
        self.volatility = volatility
        self.participation_rate = participation_rate
        self.permanent_impact = permanent_impact
        self.temporary_impact = temporary_impact
    
    def calculate_slippage(self, price: float, quantity: int, 
                          volume: Optional[float] = None) -> float:
        """
        Calculate square-root model slippage.
        
        Impact = sigma * sqrt(participation_rate) * (permanent + temporary)
        where sigma is volatility and participation_rate is order/volume ratio
        """
        if volume is None or volume == 0:
            # Default participation rate if no volume
            participation = self.participation_rate
        else:
            participation = abs(quantity) / volume
        
        # Square root impact
        impact_factor = np.sqrt(participation)
        
        # Total impact (permanent + temporary)
        total_impact = (self.permanent_impact + self.temporary_impact)
        
        # Calculate slippage
        slippage = price * self.volatility * impact_factor * total_impact
        
        return abs(slippage)


class AdaptiveSlippage(SlippageModel):
    """
    Adaptive slippage model that adjusts based on market conditions.
    
    Combines multiple factors:
    - Base slippage
    - Volume impact
    - Volatility adjustment
    - Time-of-day effects
    """
    
    def __init__(self, base_slippage: float = 0.0002,
                 volume_sensitivity: float = 0.5,
                 volatility_sensitivity: float = 0.3):
        """
        Initialize adaptive slippage model.
        
        Args:
            base_slippage: Base slippage rate
            volume_sensitivity: Sensitivity to volume (0-1)
            volatility_sensitivity: Sensitivity to volatility (0-1)
        """
        self.base_slippage = base_slippage
        self.volume_sensitivity = volume_sensitivity
        self.volatility_sensitivity = volatility_sensitivity
        self.recent_volatility = None
    
    def update_volatility(self, volatility: float):
        """Update recent volatility estimate."""
        self.recent_volatility = volatility
    
    def calculate_slippage(self, price: float, quantity: int, 
                          volume: Optional[float] = None) -> float:
        """Calculate adaptive slippage."""
        # Base component
        slippage = price * self.base_slippage
        
        # Volume component
        if volume is not None and volume > 0:
            volume_ratio = abs(quantity) / volume
            volume_impact = price * self.volume_sensitivity * volume_ratio
            slippage += volume_impact
        
        # Volatility component
        if self.recent_volatility is not None:
            vol_adjustment = price * self.volatility_sensitivity * self.recent_volatility
            slippage += vol_adjustment
        
        return abs(slippage)

"""Latency modeling for realistic order execution delays."""
from abc import ABC, abstractmethod
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Optional


class LatencyModel(ABC):
    """
    Abstract base class for latency models.
    
    Latency represents the delay between signal generation and order execution.
    """
    
    @abstractmethod
    def get_latency(self) -> float:
        """
        Get latency in seconds.
        
        Returns:
            Latency in seconds
        """
        pass


class FixedLatency(LatencyModel):
    """
    Fixed latency model - constant delay.
    
    Useful for modeling predictable system delays or creating
    baseline scenarios.
    """
    
    def __init__(self, latency_seconds: float = 0.001):
        """
        Initialize fixed latency model.
        
        Args:
            latency_seconds: Latency in seconds (default 1ms)
        """
        self.latency_seconds = latency_seconds
    
    def get_latency(self) -> float:
        """Return fixed latency."""
        return self.latency_seconds


class VariableLatency(LatencyModel):
    """
    Variable latency model with random delays.
    
    Models realistic network and system latencies with statistical
    distribution (normal, exponential, or uniform).
    """
    
    def __init__(self, 
                 mean_latency: float = 0.005,
                 std_dev: float = 0.002,
                 distribution: str = 'normal',
                 min_latency: float = 0.001,
                 max_latency: float = 0.050):
        """
        Initialize variable latency model.
        
        Args:
            mean_latency: Mean latency in seconds
            std_dev: Standard deviation in seconds
            distribution: 'normal', 'exponential', or 'uniform'
            min_latency: Minimum latency bound
            max_latency: Maximum latency bound
        """
        self.mean_latency = mean_latency
        self.std_dev = std_dev
        self.distribution = distribution
        self.min_latency = min_latency
        self.max_latency = max_latency
    
    def get_latency(self) -> float:
        """
        Sample latency from distribution.
        
        Returns:
            Latency in seconds
        """
        if self.distribution == 'normal':
            latency = np.random.normal(self.mean_latency, self.std_dev)
        elif self.distribution == 'exponential':
            latency = np.random.exponential(self.mean_latency)
        elif self.distribution == 'uniform':
            latency = np.random.uniform(self.min_latency, self.max_latency)
        else:
            raise ValueError(f"Unknown distribution: {self.distribution}")
        
        # Clamp to bounds
        return max(self.min_latency, min(self.max_latency, latency))


class TimeOfDayLatency(LatencyModel):
    """
    Latency model that varies by time of day.
    
    Models realistic patterns where latency may be higher during
    market open/close or other high-activity periods.
    """
    
    def __init__(self,
                 base_latency: float = 0.003,
                 peak_hours_multiplier: float = 2.0,
                 peak_start_hour: int = 9,
                 peak_end_hour: int = 10):
        """
        Initialize time-of-day latency model.
        
        Args:
            base_latency: Base latency during normal hours
            peak_hours_multiplier: Multiplier during peak hours
            peak_start_hour: Start of peak period (hour)
            peak_end_hour: End of peak period (hour)
        """
        self.base_latency = base_latency
        self.peak_multiplier = peak_hours_multiplier
        self.peak_start = peak_start_hour
        self.peak_end = peak_end_hour
        self.current_time = None
    
    def set_current_time(self, current_time: datetime):
        """Update current time for latency calculation."""
        self.current_time = current_time
    
    def get_latency(self) -> float:
        """
        Calculate latency based on time of day.
        
        Returns:
            Latency in seconds
        """
        if self.current_time is None:
            return self.base_latency
        
        hour = self.current_time.hour
        
        # Check if in peak hours
        if self.peak_start <= hour < self.peak_end:
            return self.base_latency * self.peak_multiplier
        
        return self.base_latency

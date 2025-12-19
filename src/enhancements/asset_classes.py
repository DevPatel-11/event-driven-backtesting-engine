"""Support for multiple asset classes in backtesting."""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd


class AssetClass(Enum):
    """Enumeration of supported asset classes."""
    EQUITY = "equity"
    FUTURES = "futures"
    OPTIONS = "options"
    FOREX = "forex"
    CRYPTO = "crypto"
    FIXED_INCOME = "fixed_income"


@dataclass
class AssetSpecification:
    """
    Specification for an asset in the portfolio.
    
    Attributes:
        symbol: Asset symbol
        asset_class: Type of asset
        multiplier: Contract multiplier (for futures/options)
        tick_size: Minimum price movement
        currency: Asset currency
        margin_requirement: Margin requirement as decimal (e.g., 0.5 for 50%)
    """
    symbol: str
    asset_class: AssetClass
    multiplier: float = 1.0
    tick_size: float = 0.01
    currency: str = "USD"
    margin_requirement: float = 1.0


class MultiAssetPortfolio:
    """
    Portfolio manager supporting multiple asset classes.
    
    This class extends the basic portfolio to handle different asset types
    with varying characteristics like contract multipliers, margin requirements,
    and currency conversions.
    """
    
    def __init__(self, initial_capital: float = 100000.0, base_currency: str = "USD"):
        """
        Initialize multi-asset portfolio.
        
        Args:
            initial_capital: Starting capital
            base_currency: Base currency for portfolio valuation
        """
        self.initial_capital = initial_capital
        self.base_currency = base_currency
        self.current_capital = initial_capital
        
        # Track assets by symbol
        self.asset_specs: Dict[str, AssetSpecification] = {}
        self.positions: Dict[str, int] = {}  # symbol -> quantity
        self.entry_prices: Dict[str, float] = {}  # symbol -> avg entry price
        
        # Track performance
        self.equity_curve = [initial_capital]
        self.trade_log = []
        
        # FX rates for currency conversion (symbol pair -> rate)
        self.fx_rates: Dict[str, float] = {}
    
    def register_asset(self, asset_spec: AssetSpecification):
        """
        Register an asset with its specifications.
        
        Args:
            asset_spec: Asset specification
        """
        self.asset_specs[asset_spec.symbol] = asset_spec
        if asset_spec.symbol not in self.positions:
            self.positions[asset_spec.symbol] = 0
    
    def update_fx_rate(self, currency_pair: str, rate: float):
        """
        Update foreign exchange rate.
        
        Args:
            currency_pair: Currency pair (e.g., 'EUR/USD')
            rate: Exchange rate
        """
        self.fx_rates[currency_pair] = rate
    
    def convert_to_base_currency(self, amount: float, currency: str) -> float:
        """
        Convert amount to base currency.
        
        Args:
            amount: Amount in source currency
            currency: Source currency
            
        Returns:
            Amount in base currency
        """
        if currency == self.base_currency:
            return amount
        
        pair = f"{currency}/{self.base_currency}"
        if pair in self.fx_rates:
            return amount * self.fx_rates[pair]
        
        # If direct pair not available, try inverse
        inverse_pair = f"{self.base_currency}/{currency}"
        if inverse_pair in self.fx_rates:
            return amount / self.fx_rates[inverse_pair]
        
        # Default to 1:1 if no rate available (with warning)
        print(f"Warning: No FX rate for {pair}, assuming 1:1")
        return amount
    
    def calculate_position_value(self, symbol: str, current_price: float) -> float:
        """
        Calculate current value of a position.
        
        Args:
            symbol: Asset symbol
            current_price: Current market price
            
        Returns:
            Position value in base currency
        """
        if symbol not in self.asset_specs:
            raise ValueError(f"Asset {symbol} not registered")
        
        spec = self.asset_specs[symbol]
        quantity = self.positions.get(symbol, 0)
        
        # Calculate value considering multiplier
        value = quantity * current_price * spec.multiplier
        
        # Convert to base currency
        return self.convert_to_base_currency(value, spec.currency)
    
    def calculate_required_margin(self, symbol: str, quantity: int, price: float) -> float:
        """
        Calculate required margin for a position.
        
        Args:
            symbol: Asset symbol
            quantity: Position quantity
            price: Entry price
            
        Returns:
            Required margin in base currency
        """
        if symbol not in self.asset_specs:
            raise ValueError(f"Asset {symbol} not registered")
        
        spec = self.asset_specs[symbol]
        position_value = abs(quantity) * price * spec.multiplier
        margin = position_value * spec.margin_requirement
        
        return self.convert_to_base_currency(margin, spec.currency)
    
    def execute_trade(self, symbol: str, quantity: int, price: float, 
                     commission: float = 0.0, timestamp=None):
        """
        Execute a trade and update positions.
        
        Args:
            symbol: Asset symbol
            quantity: Trade quantity (positive=buy, negative=sell)
            price: Execution price
            commission: Commission cost
            timestamp: Trade timestamp
        """
        if symbol not in self.asset_specs:
            raise ValueError(f"Asset {symbol} not registered")
        
        spec = self.asset_specs[symbol]
        
        # Calculate trade value
        trade_value = quantity * price * spec.multiplier
        trade_value_base = self.convert_to_base_currency(trade_value, spec.currency)
        commission_base = self.convert_to_base_currency(commission, spec.currency)
        
        # Check margin requirements
        required_margin = self.calculate_required_margin(symbol, quantity, price)
        if required_margin > self.current_capital:
            raise ValueError(f"Insufficient margin: need {required_margin}, have {self.current_capital}")
        
        # Update position
        old_position = self.positions.get(symbol, 0)
        new_position = old_position + quantity
        self.positions[symbol] = new_position
        
        # Update entry price (weighted average for additions)
        if new_position != 0:
            if old_position == 0:
                self.entry_prices[symbol] = price
            elif (old_position > 0 and quantity > 0) or (old_position < 0 and quantity < 0):
                # Adding to position
                total_cost = (old_position * self.entry_prices[symbol] + quantity * price)
                self.entry_prices[symbol] = total_cost / new_position
        
        # Update capital (subtract cost and commission)
        self.current_capital -= (trade_value_base + commission_base)
        
        # Log trade
        self.trade_log.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'commission': commission,
            'position': new_position
        })
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value.
        
        Args:
            current_prices: Dictionary of symbol -> current price
            
        Returns:
            Total portfolio value in base currency
        """
        total_value = self.current_capital
        
        for symbol, quantity in self.positions.items():
            if quantity != 0 and symbol in current_prices:
                position_value = self.calculate_position_value(symbol, current_prices[symbol])
                total_value += position_value
        
        return total_value
    
    def get_pnl_by_asset(self, current_prices: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate profit/loss for each asset.
        
        Args:
            current_prices: Dictionary of symbol -> current price
            
        Returns:
            Dictionary of symbol -> PnL in base currency
        """
        pnl_by_asset = {}
        
        for symbol, quantity in self.positions.items():
            if quantity == 0:
                continue
            
            if symbol not in current_prices or symbol not in self.entry_prices:
                continue
            
            spec = self.asset_specs[symbol]
            entry_price = self.entry_prices[symbol]
            current_price = current_prices[symbol]
            
            # Calculate P&L
            pnl = quantity * (current_price - entry_price) * spec.multiplier
            pnl_base = self.convert_to_base_currency(pnl, spec.currency)
            pnl_by_asset[symbol] = pnl_base
        
        return pnl_by_asset
    
    def get_exposure_by_asset_class(self, current_prices: Dict[str, float]) -> Dict[AssetClass, float]:
        """
        Calculate exposure by asset class.
        
        Args:
            current_prices: Dictionary of symbol -> current price
            
        Returns:
            Dictionary of asset_class -> total exposure
        """
        exposure = {ac: 0.0 for ac in AssetClass}
        
        for symbol, quantity in self.positions.items():
            if quantity != 0 and symbol in current_prices:
                spec = self.asset_specs[symbol]
                position_value = abs(self.calculate_position_value(symbol, current_prices[symbol]))
                exposure[spec.asset_class] += position_value
        
        return exposure

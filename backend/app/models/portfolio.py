"""
Portfolio and holdings related models.

Contains SQLAlchemy models for portfolios, holdings, and transactions.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, Numeric, Integer, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Portfolio(Base):
    """Portfolio model for managing investment portfolios."""
    
    __tablename__ = "portfolios"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Portfolio settings
    currency = Column(String(3), default="USD", nullable=False)
    benchmark_symbol = Column(String(20), nullable=True)
    risk_tolerance = Column(String(20), default="moderate", nullable=False)
    
    # Portfolio metrics (cached for performance)
    total_value = Column(Numeric(15, 2), default=0, nullable=False)
    total_cost = Column(Numeric(15, 2), default=0, nullable=False)
    total_gain_loss = Column(Numeric(15, 2), default=0, nullable=False)
    total_gain_loss_percent = Column(Numeric(8, 4), default=0, nullable=False)
    
    # Portfolio settings
    settings = Column(JSON, default=dict, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_rebalanced = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("PortfolioTransaction", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Portfolio(id={self.id}, name={self.name}, user_id={self.user_id})>"
    
    @property
    def holding_count(self) -> int:
        """Get number of holdings in portfolio."""
        return len(self.holdings)
    
    @property
    def is_profitable(self) -> bool:
        """Check if portfolio is profitable."""
        return self.total_gain_loss > 0


class PortfolioHolding(Base):
    """Portfolio holding model for individual stock positions."""
    
    __tablename__ = "portfolio_holdings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Stock information
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(200), nullable=True)
    exchange = Column(String(20), nullable=True)
    
    # Position information
    shares = Column(Numeric(15, 6), nullable=False)
    average_price = Column(Numeric(10, 4), nullable=False)
    current_price = Column(Numeric(10, 4), nullable=True)
    market_value = Column(Numeric(15, 2), nullable=True)
    
    # Cost basis
    total_cost = Column(Numeric(15, 2), nullable=False)
    unrealized_gain_loss = Column(Numeric(15, 2), nullable=True)
    unrealized_gain_loss_percent = Column(Numeric(8, 4), nullable=True)
    
    # Position metadata
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    market_cap = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_price_update = Column(DateTime, nullable=True)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    
    def __repr__(self) -> str:
        return f"<PortfolioHolding(id={self.id}, symbol={self.symbol}, shares={self.shares})>"
    
    @property
    def allocation_percent(self) -> Optional[Decimal]:
        """Get position allocation as percentage of portfolio."""
        if self.portfolio and self.portfolio.total_value > 0:
            return (self.market_value / self.portfolio.total_value) * 100
        return None
    
    @property
    def is_profitable(self) -> bool:
        """Check if position is profitable."""
        return self.unrealized_gain_loss and self.unrealized_gain_loss > 0


class PortfolioTransaction(Base):
    """Portfolio transaction model for tracking buy/sell transactions."""
    
    __tablename__ = "portfolio_transactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Transaction information
    symbol = Column(String(20), nullable=False, index=True)
    transaction_type = Column(String(10), nullable=False, index=True)  # buy, sell, dividend, split
    shares = Column(Numeric(15, 6), nullable=False)
    price = Column(Numeric(10, 4), nullable=False)
    commission = Column(Numeric(10, 2), default=0, nullable=False)
    fees = Column(Numeric(10, 2), default=0, nullable=False)
    
    # Transaction details
    total_amount = Column(Numeric(15, 2), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    
    # Additional metadata
    order_id = Column(String(100), nullable=True)
    broker = Column(String(100), nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    
    def __repr__(self) -> str:
        return f"<PortfolioTransaction(id={self.id}, symbol={self.symbol}, type={self.transaction_type})>"
    
    @property
    def net_amount(self) -> Decimal:
        """Get net transaction amount after fees."""
        return self.total_amount - self.commission - self.fees


class PortfolioPerformance(Base):
    """Portfolio performance model for storing historical performance data."""
    
    __tablename__ = "portfolio_performance"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Performance data
    date = Column(DateTime, nullable=False, index=True)
    total_value = Column(Numeric(15, 2), nullable=False)
    total_cost = Column(Numeric(15, 2), nullable=False)
    daily_return = Column(Numeric(8, 6), nullable=True)
    cumulative_return = Column(Numeric(8, 6), nullable=True)
    
    # Risk metrics
    volatility = Column(Numeric(8, 6), nullable=True)
    sharpe_ratio = Column(Numeric(8, 4), nullable=True)
    max_drawdown = Column(Numeric(8, 6), nullable=True)
    
    # Benchmark comparison
    benchmark_return = Column(Numeric(8, 6), nullable=True)
    alpha = Column(Numeric(8, 6), nullable=True)
    beta = Column(Numeric(8, 4), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<PortfolioPerformance(id={self.id}, portfolio_id={self.portfolio_id}, date={self.date})>"


class PortfolioAlert(Base):
    """Portfolio alert model for price and performance alerts."""
    
    __tablename__ = "portfolio_alerts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Alert information
    symbol = Column(String(20), nullable=True, index=True)  # None for portfolio-wide alerts
    alert_type = Column(String(50), nullable=False, index=True)  # price, performance, news, etc.
    condition = Column(String(20), nullable=False)  # above, below, equals
    threshold_value = Column(Numeric(15, 4), nullable=False)
    
    # Alert settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_triggered = Column(Boolean, default=False, nullable=False)
    triggered_at = Column(DateTime, nullable=True)
    
    # Notification settings
    email_notification = Column(Boolean, default=True, nullable=False)
    push_notification = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<PortfolioAlert(id={self.id}, portfolio_id={self.portfolio_id}, type={self.alert_type})>"


class TaxLot(Base):
    """Tax lot model for cost basis tracking."""
    
    __tablename__ = "tax_lots"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("portfolio_transactions.id"), nullable=False, index=True)
    
    # Tax lot information
    symbol = Column(String(20), nullable=False, index=True)
    shares = Column(Numeric(15, 6), nullable=False)
    cost_basis = Column(Numeric(15, 2), nullable=False)
    purchase_date = Column(DateTime, nullable=False, index=True)
    
    # Current status
    remaining_shares = Column(Numeric(15, 6), nullable=False)
    current_price = Column(Numeric(10, 4), nullable=True)
    current_value = Column(Numeric(15, 2), nullable=True)
    unrealized_gain_loss = Column(Numeric(15, 2), nullable=True)
    unrealized_gain_loss_percent = Column(Numeric(8, 4), nullable=True)
    
    # Tax information
    holding_period_days = Column(Integer, nullable=True)
    is_long_term = Column(Boolean, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    portfolio = relationship("Portfolio")
    transaction = relationship("PortfolioTransaction")
    
    def __repr__(self) -> str:
        return f"<TaxLot(id={self.id}, symbol={self.symbol}, shares={self.shares})>"


class PortfolioRiskMetrics(Base):
    """Portfolio risk metrics model for storing calculated risk data."""
    
    __tablename__ = "portfolio_risk_metrics"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Risk metrics
    date = Column(DateTime, nullable=False, index=True)
    beta = Column(Numeric(8, 4), nullable=True)
    alpha = Column(Numeric(8, 6), nullable=True)
    tracking_error = Column(Numeric(8, 6), nullable=True)
    information_ratio = Column(Numeric(8, 4), nullable=True)
    treynor_ratio = Column(Numeric(8, 4), nullable=True)
    jensen_alpha = Column(Numeric(8, 6), nullable=True)
    downside_deviation = Column(Numeric(8, 6), nullable=True)
    upside_capture = Column(Numeric(8, 4), nullable=True)
    downside_capture = Column(Numeric(8, 4), nullable=True)
    correlation_with_benchmark = Column(Numeric(8, 4), nullable=True)
    
    # VaR metrics
    var_95 = Column(Numeric(8, 6), nullable=True)
    var_99 = Column(Numeric(8, 6), nullable=True)
    cvar_95 = Column(Numeric(8, 6), nullable=True)
    cvar_99 = Column(Numeric(8, 6), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<PortfolioRiskMetrics(id={self.id}, portfolio_id={self.portfolio_id}, date={self.date})>"


class PortfolioAllocation(Base):
    """Portfolio allocation model for storing allocation data."""
    
    __tablename__ = "portfolio_allocations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Allocation data
    date = Column(DateTime, nullable=False, index=True)
    allocation_type = Column(String(50), nullable=False, index=True)  # sector, industry, market_cap, geographic
    allocation_data = Column(JSON, nullable=False)  # {"Technology": 0.3, "Healthcare": 0.2, ...}
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<PortfolioAllocation(id={self.id}, portfolio_id={self.portfolio_id}, type={self.allocation_type})>"


class PortfolioOptimization(Base):
    """Portfolio optimization model for storing optimization results."""
    
    __tablename__ = "portfolio_optimizations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Optimization parameters
    optimization_method = Column(String(50), nullable=False)  # markowitz, black_litterman, etc.
    constraints = Column(JSON, nullable=False)
    risk_free_rate = Column(Numeric(8, 6), nullable=False)
    
    # Optimization results
    optimal_weights = Column(JSON, nullable=False)  # {"AAPL": 0.3, "MSFT": 0.2, ...}
    expected_return = Column(Numeric(8, 6), nullable=False)
    expected_risk = Column(Numeric(8, 6), nullable=False)
    sharpe_ratio = Column(Numeric(8, 4), nullable=False)
    efficient_frontier = Column(JSON, nullable=True)
    
    # Metadata
    calculation_time = Column(Numeric(8, 3), nullable=True)  # seconds
    is_applied = Column(Boolean, default=False, nullable=False)
    applied_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<PortfolioOptimization(id={self.id}, portfolio_id={self.portfolio_id}, method={self.optimization_method})>"


class PortfolioRebalancing(Base):
    """Portfolio rebalancing model for tracking rebalancing events."""
    
    __tablename__ = "portfolio_rebalancings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Rebalancing information
    rebalancing_type = Column(String(50), nullable=False)  # threshold, scheduled, optimization
    target_weights = Column(JSON, nullable=True)
    rebalancing_threshold = Column(Numeric(8, 4), nullable=True)
    
    # Rebalancing results
    trades_executed = Column(JSON, nullable=False)  # List of trades made
    total_trades = Column(Integer, nullable=False)
    estimated_cost = Column(Numeric(15, 2), nullable=True)
    actual_cost = Column(Numeric(15, 2), nullable=True)
    rebalancing_ratio = Column(Numeric(8, 4), nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, default="pending")  # pending, completed, failed
    executed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<PortfolioRebalancing(id={self.id}, portfolio_id={self.portfolio_id}, type={self.rebalancing_type})>"


# Add indexes for better performance
Index('idx_portfolio_user_created', Portfolio.user_id, Portfolio.created_at)
Index('idx_holding_portfolio_symbol', PortfolioHolding.portfolio_id, PortfolioHolding.symbol)
Index('idx_transaction_portfolio_date', PortfolioTransaction.portfolio_id, PortfolioTransaction.date)
Index('idx_performance_portfolio_date', PortfolioPerformance.portfolio_id, PortfolioPerformance.date)
Index('idx_risk_metrics_portfolio_date', PortfolioRiskMetrics.portfolio_id, PortfolioRiskMetrics.date)
Index('idx_tax_lot_portfolio_symbol', TaxLot.portfolio_id, TaxLot.symbol)

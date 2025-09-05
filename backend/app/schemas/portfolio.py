"""
Portfolio management related Pydantic schemas.

Contains schemas for portfolios, holdings, transactions, and financial calculations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, validator, root_validator


# Enums
class TransactionType(str, Enum):
    """Transaction type enumeration."""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    SPLIT = "split"
    MERGER = "merger"
    SPINOFF = "spinoff"
    RIGHTS = "rights"
    WARRANT = "warrant"


class RiskTolerance(str, Enum):
    """Risk tolerance enumeration."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class AlertType(str, Enum):
    """Alert type enumeration."""
    PRICE = "price"
    PERFORMANCE = "performance"
    VOLUME = "volume"
    NEWS = "news"
    TECHNICAL = "technical"
    RISK = "risk"


class AlertCondition(str, Enum):
    """Alert condition enumeration."""
    ABOVE = "above"
    BELOW = "below"
    EQUALS = "equals"
    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"


# Base schemas
class PortfolioBase(BaseModel):
    """Base portfolio schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    currency: str = Field(default="USD", max_length=3)
    benchmark_symbol: Optional[str] = Field(None, max_length=20)
    risk_tolerance: RiskTolerance = Field(default=RiskTolerance.MODERATE)
    settings: Dict[str, Any] = Field(default_factory=dict)
    is_public: bool = False


class PortfolioCreate(PortfolioBase):
    """Portfolio creation schema."""
    pass


class PortfolioUpdate(BaseModel):
    """Portfolio update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    currency: Optional[str] = Field(None, max_length=3)
    benchmark_symbol: Optional[str] = Field(None, max_length=20)
    risk_tolerance: Optional[RiskTolerance] = None
    settings: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class PortfolioResponse(PortfolioBase):
    """Portfolio response schema."""
    id: UUID
    user_id: UUID
    total_value: Decimal
    total_cost: Decimal
    total_gain_loss: Decimal
    total_gain_loss_percent: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_rebalanced: Optional[datetime]
    holding_count: int
    
    class Config:
        from_attributes = True


class PortfolioHoldingBase(BaseModel):
    """Base portfolio holding schema."""
    symbol: str = Field(..., min_length=1, max_length=20)
    name: Optional[str] = Field(None, max_length=200)
    exchange: Optional[str] = Field(None, max_length=20)
    shares: Decimal = Field(..., gt=0)
    average_price: Decimal = Field(..., gt=0)
    current_price: Optional[Decimal] = Field(None, gt=0)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[str] = Field(None, max_length=20)


class PortfolioHoldingCreate(PortfolioHoldingBase):
    """Portfolio holding creation schema."""
    pass


class PortfolioHoldingUpdate(BaseModel):
    """Portfolio holding update schema."""
    shares: Optional[Decimal] = Field(None, gt=0)
    average_price: Optional[Decimal] = Field(None, gt=0)
    current_price: Optional[Decimal] = Field(None, gt=0)
    name: Optional[str] = Field(None, max_length=200)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[str] = Field(None, max_length=20)


class PortfolioHoldingResponse(PortfolioHoldingBase):
    """Portfolio holding response schema."""
    id: UUID
    portfolio_id: UUID
    market_value: Optional[Decimal]
    total_cost: Decimal
    unrealized_gain_loss: Optional[Decimal]
    unrealized_gain_loss_percent: Optional[Decimal]
    allocation_percent: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    last_price_update: Optional[datetime]
    
    class Config:
        from_attributes = True


class PortfolioTransactionBase(BaseModel):
    """Base portfolio transaction schema."""
    symbol: str = Field(..., min_length=1, max_length=20)
    transaction_type: TransactionType
    shares: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    commission: Decimal = Field(default=0, ge=0)
    fees: Decimal = Field(default=0, ge=0)
    date: datetime
    notes: Optional[str] = None
    order_id: Optional[str] = Field(None, max_length=100)
    broker: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None


class PortfolioTransactionCreate(PortfolioTransactionBase):
    """Portfolio transaction creation schema."""
    pass


class PortfolioTransactionUpdate(BaseModel):
    """Portfolio transaction update schema."""
    shares: Optional[Decimal] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, gt=0)
    commission: Optional[Decimal] = Field(None, ge=0)
    fees: Optional[Decimal] = Field(None, ge=0)
    date: Optional[datetime] = None
    notes: Optional[str] = None
    order_id: Optional[str] = Field(None, max_length=100)
    broker: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None


class PortfolioTransactionResponse(PortfolioTransactionBase):
    """Portfolio transaction response schema."""
    id: UUID
    portfolio_id: UUID
    total_amount: Decimal
    net_amount: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Financial calculation schemas
class PerformanceMetrics(BaseModel):
    """Portfolio performance metrics schema."""
    total_return: Decimal
    annualized_return: Decimal
    volatility: Decimal
    sharpe_ratio: Optional[Decimal]
    sortino_ratio: Optional[Decimal]
    calmar_ratio: Optional[Decimal]
    max_drawdown: Decimal
    max_drawdown_duration: int  # days
    win_rate: Decimal
    profit_factor: Decimal
    var_95: Optional[Decimal]
    var_99: Optional[Decimal]
    cvar_95: Optional[Decimal]
    cvar_99: Optional[Decimal]


class RiskMetrics(BaseModel):
    """Portfolio risk metrics schema."""
    beta: Decimal
    alpha: Decimal
    tracking_error: Decimal
    information_ratio: Decimal
    treynor_ratio: Decimal
    jensen_alpha: Decimal
    downside_deviation: Decimal
    upside_capture: Decimal
    downside_capture: Decimal
    correlation_with_benchmark: Decimal


class AllocationMetrics(BaseModel):
    """Portfolio allocation metrics schema."""
    sector_allocation: Dict[str, Decimal]
    industry_allocation: Dict[str, Decimal]
    market_cap_allocation: Dict[str, Decimal]
    geographic_allocation: Dict[str, Decimal]
    top_holdings: List[Dict[str, Any]]
    concentration_risk: Decimal
    diversification_ratio: Decimal


class BenchmarkComparison(BaseModel):
    """Benchmark comparison schema."""
    benchmark_symbol: str
    benchmark_return: Decimal
    excess_return: Decimal
    tracking_error: Decimal
    information_ratio: Decimal
    beta: Decimal
    alpha: Decimal
    correlation: Decimal
    outperformance_periods: int
    underperformance_periods: int


class PortfolioAnalytics(BaseModel):
    """Comprehensive portfolio analytics schema."""
    performance: PerformanceMetrics
    risk: RiskMetrics
    allocation: AllocationMetrics
    benchmark_comparison: Optional[BenchmarkComparison]
    attribution_analysis: Optional[Dict[str, Any]]
    stress_test_results: Optional[Dict[str, Any]]
    monte_carlo_results: Optional[Dict[str, Any]]


# Optimization schemas
class OptimizationConstraints(BaseModel):
    """Portfolio optimization constraints schema."""
    max_weight: Decimal = Field(default=Decimal('0.1'), ge=0, le=1)
    min_weight: Decimal = Field(default=Decimal('0.01'), ge=0, le=1)
    sector_limits: Dict[str, Decimal] = Field(default_factory=dict)
    exclude_symbols: List[str] = Field(default_factory=list)
    target_return: Optional[Decimal] = None
    max_risk: Optional[Decimal] = None
    rebalance_threshold: Decimal = Field(default=Decimal('0.05'), ge=0, le=1)


class OptimizationResult(BaseModel):
    """Portfolio optimization result schema."""
    weights: Dict[str, Decimal]
    expected_return: Decimal
    expected_risk: Decimal
    sharpe_ratio: Decimal
    efficient_frontier: List[Dict[str, Decimal]]
    optimization_method: str
    constraints_used: OptimizationConstraints
    calculation_time: float  # seconds


class RebalancingRecommendation(BaseModel):
    """Portfolio rebalancing recommendation schema."""
    symbol: str
    current_weight: Decimal
    target_weight: Decimal
    weight_difference: Decimal
    current_shares: Decimal
    target_shares: Decimal
    shares_to_trade: Decimal
    trade_type: str  # "buy" or "sell"
    estimated_cost: Decimal
    priority: int  # 1-5, 5 being highest priority


class RebalancingPlan(BaseModel):
    """Portfolio rebalancing plan schema."""
    recommendations: List[RebalancingRecommendation]
    total_trades: int
    estimated_cost: Decimal
    estimated_commission: Decimal
    rebalancing_ratio: Decimal
    one_way_turnover: Decimal
    two_way_turnover: Decimal
    tax_impact: Optional[Decimal]


# Alert schemas
class PortfolioAlertBase(BaseModel):
    """Base portfolio alert schema."""
    symbol: Optional[str] = Field(None, max_length=20)
    alert_type: AlertType
    condition: AlertCondition
    threshold_value: Decimal
    is_active: bool = True
    email_notification: bool = True
    push_notification: bool = False


class PortfolioAlertCreate(PortfolioAlertBase):
    """Portfolio alert creation schema."""
    pass


class PortfolioAlertUpdate(BaseModel):
    """Portfolio alert update schema."""
    condition: Optional[AlertCondition] = None
    threshold_value: Optional[Decimal] = None
    is_active: Optional[bool] = None
    email_notification: Optional[bool] = None
    push_notification: Optional[bool] = None


class PortfolioAlertResponse(PortfolioAlertBase):
    """Portfolio alert response schema."""
    id: UUID
    portfolio_id: UUID
    is_triggered: bool
    triggered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Performance tracking schemas
class PerformanceDataPoint(BaseModel):
    """Performance data point schema."""
    date: datetime
    portfolio_value: Decimal
    benchmark_value: Optional[Decimal]
    daily_return: Decimal
    cumulative_return: Decimal
    drawdown: Decimal


class PerformanceHistory(BaseModel):
    """Performance history schema."""
    portfolio_id: UUID
    period: str
    data_points: List[PerformanceDataPoint]
    summary_metrics: PerformanceMetrics
    benchmark_comparison: Optional[BenchmarkComparison]


# Tax lot tracking schemas
class TaxLot(BaseModel):
    """Tax lot schema for cost basis tracking."""
    id: UUID
    symbol: str
    shares: Decimal
    cost_basis: Decimal
    purchase_date: datetime
    holding_period: int  # days
    is_long_term: bool
    unrealized_gain_loss: Decimal
    unrealized_gain_loss_percent: Decimal


class TaxLotSummary(BaseModel):
    """Tax lot summary schema."""
    symbol: str
    total_shares: Decimal
    total_cost_basis: Decimal
    average_cost_basis: Decimal
    current_value: Decimal
    unrealized_gain_loss: Decimal
    unrealized_gain_loss_percent: Decimal
    long_term_shares: Decimal
    short_term_shares: Decimal
    long_term_gain_loss: Decimal
    short_term_gain_loss: Decimal
    tax_lots: List[TaxLot]


# Request/Response schemas for API endpoints
class PortfolioListResponse(BaseModel):
    """Portfolio list response schema."""
    portfolios: List[PortfolioResponse]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class PortfolioDetailResponse(BaseModel):
    """Portfolio detail response schema."""
    portfolio: PortfolioResponse
    holdings: List[PortfolioHoldingResponse]
    transactions: List[PortfolioTransactionResponse]
    analytics: Optional[PortfolioAnalytics]
    alerts: List[PortfolioAlertResponse]
    tax_lots: List[TaxLotSummary]


class HoldingsListResponse(BaseModel):
    """Holdings list response schema."""
    holdings: List[PortfolioHoldingResponse]
    total: int
    total_value: Decimal
    total_cost: Decimal
    total_gain_loss: Decimal
    total_gain_loss_percent: Decimal


class TransactionsListResponse(BaseModel):
    """Transactions list response schema."""
    transactions: List[PortfolioTransactionResponse]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class PerformanceResponse(BaseModel):
    """Performance response schema."""
    portfolio_id: UUID
    period: str
    performance: PerformanceMetrics
    risk: RiskMetrics
    benchmark_comparison: Optional[BenchmarkComparison]
    performance_history: List[PerformanceDataPoint]


class OptimizationRequest(BaseModel):
    """Portfolio optimization request schema."""
    constraints: OptimizationConstraints
    optimization_method: str = Field(default="markowitz", regex="^(markowitz|black_litterman|risk_parity|equal_weight)$")
    risk_free_rate: Decimal = Field(default=Decimal('0.02'), ge=0, le=1)
    expected_return_method: str = Field(default="historical", regex="^(historical|fundamental|technical)$")
    rebalance_frequency: str = Field(default="monthly", regex="^(daily|weekly|monthly|quarterly|annually)$")


class RebalancingRequest(BaseModel):
    """Portfolio rebalancing request schema."""
    target_weights: Optional[Dict[str, Decimal]] = None
    rebalance_threshold: Decimal = Field(default=Decimal('0.05'), ge=0, le=1)
    max_trades: Optional[int] = Field(None, ge=1, le=50)
    min_trade_amount: Decimal = Field(default=Decimal('100'), ge=0)
    consider_taxes: bool = True
    dry_run: bool = False


class ImportPortfolioRequest(BaseModel):
    """Portfolio import request schema."""
    file_format: str = Field(..., regex="^(csv|excel|json)$")
    file_content: str  # Base64 encoded file content
    mapping: Dict[str, str]  # Column mapping
    options: Dict[str, Any] = Field(default_factory=dict)


class ExportPortfolioRequest(BaseModel):
    """Portfolio export request schema."""
    format: str = Field(..., regex="^(csv|excel|pdf|json)$")
    include_transactions: bool = True
    include_performance: bool = True
    include_analytics: bool = False
    date_range: Optional[Dict[str, datetime]] = None


# WebSocket schemas
class PortfolioWebSocketMessage(BaseModel):
    """Portfolio WebSocket message schema."""
    type: str = Field(..., regex="^(portfolio_update|holding_update|performance_update|risk_update|alert_triggered)$")
    portfolio_id: UUID
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PortfolioWebSocketSubscription(BaseModel):
    """Portfolio WebSocket subscription schema."""
    portfolio_ids: List[UUID]
    event_types: List[str] = Field(default=["portfolio_update", "holding_update"])
    include_analytics: bool = False


# Error schemas
class PortfolioError(BaseModel):
    """Portfolio error schema."""
    error: str
    detail: Optional[str] = None
    portfolio_id: Optional[UUID] = None
    symbol: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationError(BaseModel):
    """Validation error schema."""
    field: str
    message: str
    value: Any


class CalculationError(BaseModel):
    """Financial calculation error schema."""
    error: str
    calculation_type: str
    parameters: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

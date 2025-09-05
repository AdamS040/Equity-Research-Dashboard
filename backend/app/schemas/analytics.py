"""
Analytics Schemas

Pydantic models for analytics API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from decimal import Decimal


# DCF Analysis Schemas
class DCFInputsSchema(BaseModel):
    """DCF Analysis Input Parameters Schema"""
    symbol: str = Field(..., description="Stock symbol")
    current_price: float = Field(..., gt=0, description="Current stock price")
    revenue: float = Field(..., gt=0, description="Current revenue")
    revenue_growth_rate: float = Field(..., ge=0, le=1, description="Revenue growth rate (0-1)")
    ebitda_margin: float = Field(..., ge=0, le=1, description="EBITDA margin (0-1)")
    tax_rate: float = Field(..., ge=0, le=1, description="Tax rate (0-1)")
    capex: float = Field(..., description="Capital expenditures")
    working_capital: float = Field(..., description="Working capital")
    terminal_growth_rate: float = Field(..., ge=0, le=0.1, description="Terminal growth rate (0-0.1)")
    beta: float = Field(..., gt=0, description="Beta coefficient")
    risk_free_rate: float = Field(..., ge=0, description="Risk-free rate")
    market_risk_premium: float = Field(..., ge=0, description="Market risk premium")
    debt_to_equity: float = Field(..., ge=0, description="Debt-to-equity ratio")
    cost_of_debt: float = Field(..., ge=0, description="Cost of debt")
    projection_years: int = Field(5, ge=1, le=20, description="Projection years")


class DCFProjectionSchema(BaseModel):
    """DCF Projection Schema"""
    year: int
    revenue: float
    ebitda: float
    ebit: float
    tax: float
    nopat: float
    depreciation: float
    capex: float
    working_capital_change: float
    free_cash_flow: float
    present_value: float


class DCFResultsSchema(BaseModel):
    """DCF Analysis Results Schema"""
    symbol: str
    fair_value: float
    upside: float
    upside_percent: float
    terminal_value: float
    projections: List[DCFProjectionSchema]
    sensitivity_analysis: Dict[str, Any]
    monte_carlo_results: Dict[str, Any]
    wacc_breakdown: Dict[str, float]


# Risk Analysis Schemas
class RiskMetricsSchema(BaseModel):
    """Risk Metrics Schema"""
    beta: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    tracking_error: float
    information_ratio: float
    calmar_ratio: float


class RiskAnalysisRequestSchema(BaseModel):
    """Risk Analysis Request Schema"""
    returns: List[float] = Field(..., min_items=30, description="Historical returns (minimum 30 data points)")
    benchmark_returns: Optional[List[float]] = Field(None, description="Benchmark returns for comparison")
    
    @validator('returns')
    def validate_returns(cls, v):
        if len(v) < 30:
            raise ValueError('At least 30 data points required for risk analysis')
        if any(not isinstance(x, (int, float)) or abs(x) > 1 for x in v):
            raise ValueError('Returns must be valid numbers between -1 and 1')
        return v


# Options Analysis Schemas
class OptionsGreeksSchema(BaseModel):
    """Options Greeks Schema"""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


class OptionsAnalysisRequestSchema(BaseModel):
    """Options Analysis Request Schema"""
    underlying_price: float = Field(..., gt=0, description="Underlying asset price")
    strike_price: float = Field(..., gt=0, description="Strike price")
    time_to_expiration: float = Field(..., gt=0, description="Time to expiration in years")
    risk_free_rate: float = Field(..., ge=0, description="Risk-free rate")
    volatility: float = Field(..., gt=0, description="Implied volatility")
    option_type: str = Field("call", regex="^(call|put)$", description="Option type (call or put)")


class OptionsAnalysisResponseSchema(BaseModel):
    """Options Analysis Response Schema"""
    underlying_price: float
    strike_price: float
    time_to_expiration: float
    option_type: str
    price: float
    greeks: OptionsGreeksSchema


# Comparable Analysis Schemas
class PeerCompanySchema(BaseModel):
    """Peer Company Schema"""
    symbol: str
    name: str
    market_cap: float
    enterprise_value: float
    revenue: float
    ebitda: float
    net_income: float
    shares_outstanding: float
    price: float
    pe: float
    pb: float
    ps: float
    ev_revenue: float
    ev_ebitda: float
    peg: float
    roe: float
    roa: float
    debt_to_equity: float
    current_ratio: float
    industry: str
    sector: str
    market_cap_category: str


class ValuationMetricSchema(BaseModel):
    """Valuation Metric Statistics Schema"""
    min: float
    max: float
    median: float
    mean: float
    percentile_25: float
    percentile_75: float
    standard_deviation: float
    count: int


class ComparableValuationSchema(BaseModel):
    """Comparable Valuation Results Schema"""
    pe_based: float
    pb_based: float
    ps_based: float
    ev_revenue_based: float
    ev_ebitda_based: float
    average: float
    median: float
    weighted_average: float
    confidence_score: float


class PeerRankingSchema(BaseModel):
    """Peer Company Ranking Schema"""
    symbol: str
    name: str
    overall_score: float
    valuation_score: float
    profitability_score: float
    growth_score: float
    financial_health_score: float
    rank: int


class ComparableAnalysisRequestSchema(BaseModel):
    """Comparable Analysis Request Schema"""
    target_company: Dict[str, Any] = Field(..., description="Target company data")
    peer_universe: List[Dict[str, Any]] = Field(..., min_items=5, description="Peer company universe")
    target_financials: Dict[str, float] = Field(..., description="Target company financials")


class ComparableAnalysisResponseSchema(BaseModel):
    """Comparable Analysis Response Schema"""
    target_company: Dict[str, Any]
    peers: List[PeerCompanySchema]
    valuation_metrics: Dict[str, ValuationMetricSchema]
    comparable_valuation: ComparableValuationSchema
    peer_rankings: List[PeerRankingSchema]
    industry_analysis: Dict[str, Any]
    analysis_metadata: Dict[str, Any]


# Backtesting Schemas
class BacktestStrategySchema(BaseModel):
    """Backtesting Strategy Schema"""
    name: str
    description: str
    parameters: Dict[str, Any]
    entry_rules: List[str]
    exit_rules: List[str]
    position_sizing: str
    max_positions: int = 10
    rebalance_frequency: str = "daily"


class BacktestTradeSchema(BaseModel):
    """Backtest Trade Schema"""
    entry_date: str
    exit_date: str
    symbol: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_percent: float
    duration: int
    reason: str


class BacktestResultsSchema(BaseModel):
    """Backtesting Results Schema"""
    strategy: BacktestStrategySchema
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    win_rate: float
    profit_factor: float
    trades: List[BacktestTradeSchema]
    monthly_returns: List[Dict[str, Any]]
    benchmark_comparison: Dict[str, Any]
    performance_metrics: Dict[str, Any]


class BacktestRequestSchema(BaseModel):
    """Backtest Request Schema"""
    strategy_name: str
    strategy_description: str
    parameters: Dict[str, Any]
    entry_rules: List[str]
    exit_rules: List[str]
    position_sizing: str
    initial_capital: float = Field(100000, gt=0)
    transaction_cost: float = Field(0.001, ge=0, le=0.1)


# Economic Indicators Schemas
class EconomicIndicatorSchema(BaseModel):
    """Economic Indicator Schema"""
    name: str
    symbol: str
    value: float
    previous_value: float
    change: float
    change_percent: float
    unit: str
    frequency: str
    last_updated: str
    source: str
    description: str
    importance: str
    country: str
    category: str


class EconomicEventSchema(BaseModel):
    """Economic Calendar Event Schema"""
    time: str
    country: str
    event: str
    importance: str
    actual: Optional[float]
    forecast: Optional[float]
    previous: Optional[float]
    unit: str
    impact: str


class MarketSentimentSchema(BaseModel):
    """Market Sentiment Schema"""
    vix: float
    vix_change: float
    fear_greed_index: float
    put_call_ratio: float
    insider_trading: float
    institutional_flow: float
    retail_flow: float
    last_updated: str


class EconomicIndicatorsResponseSchema(BaseModel):
    """Economic Indicators Response Schema"""
    country: str
    indicators: Dict[str, EconomicIndicatorSchema]
    market_sentiment: MarketSentimentSchema


# Monte Carlo Schemas
class MonteCarloRequestSchema(BaseModel):
    """Monte Carlo Simulation Request Schema"""
    initial_value: float = Field(..., gt=0, description="Initial value")
    expected_return: float = Field(..., description="Expected return")
    volatility: float = Field(..., gt=0, description="Volatility")
    time_horizon: int = Field(..., gt=0, description="Time horizon in years")
    simulations: int = Field(1000, ge=100, le=10000, description="Number of simulations")


class MonteCarloResultsSchema(BaseModel):
    """Monte Carlo Simulation Results Schema"""
    mean: float
    median: float
    percentile_5: float
    percentile_25: float
    percentile_75: float
    percentile_95: float
    probability_of_loss: float
    expected_return: float
    confidence_interval: Dict[str, float]


# Stress Testing Schemas
class StressTestRequestSchema(BaseModel):
    """Stress Test Request Schema"""
    returns: List[float] = Field(..., min_items=30, description="Historical returns")
    scenarios: Dict[str, float] = Field(..., description="Stress test scenarios")
    
    @validator('returns')
    def validate_returns(cls, v):
        if len(v) < 30:
            raise ValueError('At least 30 data points required for stress testing')
        return v


class StressTestResultsSchema(BaseModel):
    """Stress Test Results Schema"""
    scenarios: Dict[str, Dict[str, float]]
    analysis_date: str


# Generic Response Schemas
class AnalyticsResponseSchema(BaseModel):
    """Generic Analytics Response Schema"""
    success: bool
    data: Dict[str, Any]
    timestamp: str
    message: Optional[str] = None


class ErrorResponseSchema(BaseModel):
    """Error Response Schema"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: str


# Health Check Schema
class HealthCheckSchema(BaseModel):
    """Health Check Schema"""
    success: bool
    data: Dict[str, Any]
    timestamp: str

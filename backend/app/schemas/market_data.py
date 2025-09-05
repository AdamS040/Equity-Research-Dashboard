"""
Market data related Pydantic schemas.

Contains schemas for market data requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, validator


class StockBase(BaseModel):
    """Base stock schema."""
    symbol: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=200)
    exchange: str = Field(..., min_length=1, max_length=20)
    currency: str = Field(default="USD", max_length=3)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[Decimal] = None
    market_cap_category: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    is_delisted: bool = False
    ipo_date: Optional[datetime] = None


class StockCreate(StockBase):
    """Stock creation schema."""
    pass


class StockUpdate(BaseModel):
    """Stock update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[Decimal] = None
    market_cap_category: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_delisted: Optional[bool] = None


class StockResponse(StockBase):
    """Stock response schema."""
    id: UUID
    data_quality_score: Decimal
    last_data_update: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StockQuoteBase(BaseModel):
    """Base stock quote schema."""
    symbol: str = Field(..., min_length=1, max_length=20)
    price: Decimal = Field(..., gt=0)
    change: Decimal
    change_percent: Decimal
    volume: Decimal = Field(..., ge=0)
    open_price: Optional[Decimal] = None
    high_price: Optional[Decimal] = None
    low_price: Optional[Decimal] = None
    previous_close: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    pe_ratio: Optional[Decimal] = None
    eps: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    is_market_open: bool = True
    session_type: str = Field(default="regular", max_length=20)
    data_source: str = Field(..., max_length=50)
    data_quality: Decimal = Field(default=1.0, ge=0, le=1)


class StockQuoteCreate(StockQuoteBase):
    """Stock quote creation schema."""
    stock_id: UUID
    quote_time: datetime


class StockQuoteResponse(StockQuoteBase):
    """Stock quote response schema."""
    id: UUID
    stock_id: UUID
    quote_time: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockHistoricalDataBase(BaseModel):
    """Base historical data schema."""
    symbol: str = Field(..., min_length=1, max_length=20)
    date: datetime
    open_price: Decimal = Field(..., gt=0)
    high_price: Decimal = Field(..., gt=0)
    low_price: Decimal = Field(..., gt=0)
    close_price: Decimal = Field(..., gt=0)
    volume: Decimal = Field(..., ge=0)
    adjusted_open: Optional[Decimal] = None
    adjusted_high: Optional[Decimal] = None
    adjusted_low: Optional[Decimal] = None
    adjusted_close: Optional[Decimal] = None
    sma_20: Optional[Decimal] = None
    sma_50: Optional[Decimal] = None
    sma_200: Optional[Decimal] = None
    rsi_14: Optional[Decimal] = None
    data_source: str = Field(..., max_length=50)


class StockHistoricalDataCreate(StockHistoricalDataBase):
    """Historical data creation schema."""
    stock_id: UUID


class StockHistoricalDataResponse(StockHistoricalDataBase):
    """Historical data response schema."""
    id: UUID
    stock_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class MarketIndexBase(BaseModel):
    """Base market index schema."""
    symbol: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    current_value: Decimal = Field(..., gt=0)
    change: Decimal
    change_percent: Decimal
    open_value: Optional[Decimal] = None
    high_value: Optional[Decimal] = None
    low_value: Optional[Decimal] = None
    previous_close: Optional[Decimal] = None
    is_market_open: bool = True
    data_source: str = Field(..., max_length=50)


class MarketIndexCreate(MarketIndexBase):
    """Market index creation schema."""
    last_update: datetime


class MarketIndexResponse(MarketIndexBase):
    """Market index response schema."""
    id: UUID
    last_update: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SectorBase(BaseModel):
    """Base sector schema."""
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    current_value: Decimal = Field(..., gt=0)
    change: Decimal
    change_percent: Decimal
    market_cap: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    data_source: str = Field(..., max_length=50)


class SectorCreate(SectorBase):
    """Sector creation schema."""
    last_update: datetime


class SectorResponse(SectorBase):
    """Sector response schema."""
    id: UUID
    last_update: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MarketMoverBase(BaseModel):
    """Base market mover schema."""
    symbol: str = Field(..., min_length=1, max_length=20)
    name: Optional[str] = Field(None, max_length=200)
    mover_type: str = Field(..., regex="^(gainer|loser|active)$")
    price: Decimal = Field(..., gt=0)
    change: Decimal
    change_percent: Decimal
    volume: Decimal = Field(..., ge=0)
    rank: int = Field(..., ge=1)
    market_cap: Optional[Decimal] = None
    sector: Optional[str] = Field(None, max_length=100)
    data_source: str = Field(..., max_length=50)


class MarketMoverCreate(MarketMoverBase):
    """Market mover creation schema."""
    last_update: datetime


class MarketMoverResponse(MarketMoverBase):
    """Market mover response schema."""
    id: UUID
    last_update: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockNewsBase(BaseModel):
    """Base stock news schema."""
    symbol: Optional[str] = Field(None, max_length=20)
    title: str = Field(..., min_length=1, max_length=500)
    summary: Optional[str] = None
    content: Optional[str] = None
    url: str = Field(..., min_length=1, max_length=1000)
    source: str = Field(..., min_length=1, max_length=100)
    author: Optional[str] = Field(None, max_length=200)
    published_at: datetime
    sentiment_score: Optional[Decimal] = Field(None, ge=-1, le=1)
    sentiment_label: Optional[str] = Field(None, regex="^(positive|negative|neutral)$")
    confidence: Optional[Decimal] = Field(None, ge=0, le=1)
    views: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    data_source: str = Field(..., max_length=50)


class StockNewsCreate(StockNewsBase):
    """Stock news creation schema."""
    stock_id: Optional[UUID] = None


class StockNewsResponse(StockNewsBase):
    """Stock news response schema."""
    id: UUID
    stock_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MarketSentimentBase(BaseModel):
    """Base market sentiment schema."""
    fear_greed_index: Optional[Decimal] = Field(None, ge=0, le=100)
    vix: Optional[Decimal] = Field(None, ge=0)
    put_call_ratio: Optional[Decimal] = Field(None, ge=0)
    advancing_stocks: Optional[int] = Field(None, ge=0)
    declining_stocks: Optional[int] = Field(None, ge=0)
    unchanged_stocks: Optional[int] = Field(None, ge=0)
    overall_sentiment: Optional[Decimal] = Field(None, ge=-1, le=1)
    sentiment_label: Optional[str] = Field(None, regex="^(bullish|bearish|neutral)$")
    data_source: str = Field(..., max_length=50)


class MarketSentimentCreate(MarketSentimentBase):
    """Market sentiment creation schema."""
    measurement_time: datetime


class MarketSentimentResponse(MarketSentimentBase):
    """Market sentiment response schema."""
    id: UUID
    measurement_time: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class DataProviderBase(BaseModel):
    """Base data provider schema."""
    name: str = Field(..., min_length=1, max_length=100)
    base_url: str = Field(..., min_length=1, max_length=500)
    requests_per_minute: int = Field(default=60, ge=1)
    requests_per_day: int = Field(default=1000, ge=1)
    is_active: bool = True
    is_primary: bool = False
    priority: int = Field(default=1, ge=1)
    supports_quotes: bool = True
    supports_historical: bool = True
    supports_news: bool = False
    supports_sentiment: bool = False


class DataProviderCreate(DataProviderBase):
    """Data provider creation schema."""
    api_key: Optional[str] = Field(None, max_length=500)


class DataProviderUpdate(BaseModel):
    """Data provider update schema."""
    api_key: Optional[str] = Field(None, max_length=500)
    base_url: Optional[str] = Field(None, min_length=1, max_length=500)
    requests_per_minute: Optional[int] = Field(None, ge=1)
    requests_per_day: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None
    is_primary: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1)
    supports_quotes: Optional[bool] = None
    supports_historical: Optional[bool] = None
    supports_news: Optional[bool] = None
    supports_sentiment: Optional[bool] = None


class DataProviderResponse(DataProviderBase):
    """Data provider response schema."""
    id: UUID
    current_requests_minute: int
    current_requests_day: int
    last_reset_minute: Optional[datetime]
    last_reset_day: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Request/Response schemas for API endpoints

class MarketOverviewResponse(BaseModel):
    """Market overview response schema."""
    market_status: str
    market_indices: List[MarketIndexResponse]
    top_gainers: List[MarketMoverResponse]
    top_losers: List[MarketMoverResponse]
    most_active: List[MarketMoverResponse]
    market_sentiment: Optional[MarketSentimentResponse]
    last_update: datetime


class StockSearchRequest(BaseModel):
    """Stock search request schema."""
    query: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(default=10, ge=1, le=50)
    exchange: Optional[str] = None
    sector: Optional[str] = None


class StockSearchResponse(BaseModel):
    """Stock search response schema."""
    stocks: List[StockResponse]
    total: int
    query: str


class HistoricalDataRequest(BaseModel):
    """Historical data request schema."""
    symbol: str = Field(..., min_length=1, max_length=20)
    period: str = Field(default="1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$")
    interval: str = Field(default="1d", regex="^(1m|2m|5m|15m|30m|60m|90m|1h|1d|5d|1wk|1mo|3mo)$")
    
    @validator('interval')
    def validate_interval_period(cls, v, values):
        """Validate interval against period."""
        period = values.get('period', '1y')
        
        # Short periods can use shorter intervals
        if period in ['1d', '5d'] and v not in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']:
            raise ValueError(f"Interval {v} not valid for period {period}")
        
        # Long periods should use longer intervals
        if period in ['5y', '10y', 'max'] and v in ['1m', '2m', '5m', '15m', '30m']:
            raise ValueError(f"Interval {v} not recommended for period {period}")
        
        return v


class HistoricalDataResponse(BaseModel):
    """Historical data response schema."""
    symbol: str
    period: str
    interval: str
    data: List[StockHistoricalDataResponse]
    count: int
    data_source: str


class WebSocketMessage(BaseModel):
    """WebSocket message schema."""
    type: str = Field(..., regex="^(market_update|quote_update|sector_update|sentiment_update|error)$")
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebSocketSubscription(BaseModel):
    """WebSocket subscription schema."""
    type: str = Field(..., regex="^(market_data|stock_quotes|sector_data|sentiment_data)$")
    symbols: Optional[List[str]] = None
    channels: Optional[List[str]] = None


class WebSocketResponse(BaseModel):
    """WebSocket response schema."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


# Error schemas

class MarketDataError(BaseModel):
    """Market data error schema."""
    error: str
    detail: Optional[str] = None
    symbol: Optional[str] = None
    data_source: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RateLimitError(BaseModel):
    """Rate limit error schema."""
    error: str = "Rate limit exceeded"
    detail: str
    retry_after: int
    provider: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

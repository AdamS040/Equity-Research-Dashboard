"""
Market data related models.

Contains SQLAlchemy models for stocks, quotes, indices, sectors, and market data.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, Numeric, Integer, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Stock(Base):
    """Stock information model."""
    
    __tablename__ = "stocks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Stock identification
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    exchange = Column(String(20), nullable=False, index=True)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Company information
    sector = Column(String(100), nullable=True, index=True)
    industry = Column(String(100), nullable=True, index=True)
    market_cap = Column(Numeric(20, 2), nullable=True)
    market_cap_category = Column(String(20), nullable=True)  # large, mid, small, micro
    
    # Stock metadata
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Trading information
    is_active = Column(Boolean, default=True, nullable=False)
    is_delisted = Column(Boolean, default=False, nullable=False)
    ipo_date = Column(DateTime, nullable=True)
    
    # Data quality
    data_quality_score = Column(Numeric(3, 2), default=1.0, nullable=False)
    last_data_update = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    quotes = relationship("StockQuote", back_populates="stock", cascade="all, delete-orphan")
    historical_data = relationship("StockHistoricalData", back_populates="stock", cascade="all, delete-orphan")
    news = relationship("StockNews", back_populates="stock", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Stock(symbol={self.symbol}, name={self.name})>"
    
    @property
    def is_large_cap(self) -> bool:
        """Check if stock is large cap."""
        return self.market_cap_category == "large"
    
    @property
    def is_tech_stock(self) -> bool:
        """Check if stock is in technology sector."""
        return self.sector and "technology" in self.sector.lower()


class StockQuote(Base):
    """Real-time stock quote model."""
    
    __tablename__ = "stock_quotes"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False, index=True)
    
    # Quote data
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Numeric(10, 4), nullable=False)
    change = Column(Numeric(10, 4), nullable=False)
    change_percent = Column(Numeric(8, 4), nullable=False)
    volume = Column(Numeric(15, 0), nullable=False)
    
    # Price levels
    open_price = Column(Numeric(10, 4), nullable=True)
    high_price = Column(Numeric(10, 4), nullable=True)
    low_price = Column(Numeric(10, 4), nullable=True)
    previous_close = Column(Numeric(10, 4), nullable=True)
    
    # Market data
    market_cap = Column(Numeric(20, 2), nullable=True)
    pe_ratio = Column(Numeric(8, 2), nullable=True)
    eps = Column(Numeric(8, 4), nullable=True)
    dividend_yield = Column(Numeric(6, 4), nullable=True)
    
    # Trading session
    is_market_open = Column(Boolean, default=True, nullable=False)
    session_type = Column(String(20), default="regular", nullable=False)  # regular, pre, after
    
    # Data source
    data_source = Column(String(50), nullable=False)
    data_quality = Column(Numeric(3, 2), default=1.0, nullable=False)
    
    # Timestamps
    quote_time = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    stock = relationship("Stock", back_populates="quotes")
    
    def __repr__(self) -> str:
        return f"<StockQuote(symbol={self.symbol}, price={self.price})>"
    
    @property
    def is_gain(self) -> bool:
        """Check if stock is gaining."""
        return self.change > 0
    
    @property
    def is_loss(self) -> bool:
        """Check if stock is losing."""
        return self.change < 0


class StockHistoricalData(Base):
    """Historical stock price data model."""
    
    __tablename__ = "stock_historical_data"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False, index=True)
    
    # Historical data
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # OHLCV data
    open_price = Column(Numeric(10, 4), nullable=False)
    high_price = Column(Numeric(10, 4), nullable=False)
    low_price = Column(Numeric(10, 4), nullable=False)
    close_price = Column(Numeric(10, 4), nullable=False)
    volume = Column(Numeric(15, 0), nullable=False)
    
    # Adjusted prices
    adjusted_open = Column(Numeric(10, 4), nullable=True)
    adjusted_high = Column(Numeric(10, 4), nullable=True)
    adjusted_low = Column(Numeric(10, 4), nullable=True)
    adjusted_close = Column(Numeric(10, 4), nullable=True)
    
    # Technical indicators (cached)
    sma_20 = Column(Numeric(10, 4), nullable=True)
    sma_50 = Column(Numeric(10, 4), nullable=True)
    sma_200 = Column(Numeric(10, 4), nullable=True)
    rsi_14 = Column(Numeric(6, 2), nullable=True)
    
    # Data source
    data_source = Column(String(50), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    stock = relationship("Stock", back_populates="historical_data")
    
    # Indexes
    __table_args__ = (
        Index('idx_stock_date', 'stock_id', 'date'),
        Index('idx_symbol_date', 'symbol', 'date'),
    )
    
    def __repr__(self) -> str:
        return f"<StockHistoricalData(symbol={self.symbol}, date={self.date})>"


class MarketIndex(Base):
    """Market index model (S&P 500, NASDAQ, etc.)."""
    
    __tablename__ = "market_indices"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Index identification
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Current values
    current_value = Column(Numeric(12, 2), nullable=False)
    change = Column(Numeric(12, 2), nullable=False)
    change_percent = Column(Numeric(8, 4), nullable=False)
    
    # Session data
    open_value = Column(Numeric(12, 2), nullable=True)
    high_value = Column(Numeric(12, 2), nullable=True)
    low_value = Column(Numeric(12, 2), nullable=True)
    previous_close = Column(Numeric(12, 2), nullable=True)
    
    # Market status
    is_market_open = Column(Boolean, default=True, nullable=False)
    
    # Data source
    data_source = Column(String(50), nullable=False)
    
    # Timestamps
    last_update = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<MarketIndex(symbol={self.symbol}, value={self.current_value})>"


class Sector(Base):
    """Market sector model."""
    
    __tablename__ = "sectors"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Sector information
    name = Column(String(100), unique=True, nullable=False, index=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Performance data
    current_value = Column(Numeric(12, 2), nullable=False)
    change = Column(Numeric(12, 2), nullable=False)
    change_percent = Column(Numeric(8, 4), nullable=False)
    
    # Market data
    market_cap = Column(Numeric(20, 2), nullable=True)
    volume = Column(Numeric(15, 0), nullable=True)
    
    # Data source
    data_source = Column(String(50), nullable=False)
    
    # Timestamps
    last_update = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Sector(name={self.name}, change_percent={self.change_percent})>"


class MarketMover(Base):
    """Market movers model (gainers, losers, most active)."""
    
    __tablename__ = "market_movers"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Mover information
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(200), nullable=True)
    mover_type = Column(String(20), nullable=False, index=True)  # gainer, loser, active
    
    # Performance data
    price = Column(Numeric(10, 4), nullable=False)
    change = Column(Numeric(10, 4), nullable=False)
    change_percent = Column(Numeric(8, 4), nullable=False)
    volume = Column(Numeric(15, 0), nullable=False)
    
    # Ranking
    rank = Column(Integer, nullable=False)
    
    # Market data
    market_cap = Column(Numeric(20, 2), nullable=True)
    sector = Column(String(100), nullable=True)
    
    # Data source
    data_source = Column(String(50), nullable=False)
    
    # Timestamps
    last_update = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_mover_type_rank', 'mover_type', 'rank'),
        Index('idx_mover_type_update', 'mover_type', 'last_update'),
    )
    
    def __repr__(self) -> str:
        return f"<MarketMover(symbol={self.symbol}, type={self.mover_type}, rank={self.rank})>"


class StockNews(Base):
    """Stock news model."""
    
    __tablename__ = "stock_news"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=True, index=True)
    
    # News information
    symbol = Column(String(20), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(1000), nullable=False)
    
    # News metadata
    source = Column(String(100), nullable=False)
    author = Column(String(200), nullable=True)
    published_at = Column(DateTime, nullable=False, index=True)
    
    # Sentiment analysis
    sentiment_score = Column(Numeric(4, 2), nullable=True)  # -1 to 1
    sentiment_label = Column(String(20), nullable=True)  # positive, negative, neutral
    confidence = Column(Numeric(4, 2), nullable=True)
    
    # Engagement metrics
    views = Column(Integer, default=0, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    
    # Data source
    data_source = Column(String(50), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    stock = relationship("Stock", back_populates="news")
    
    def __repr__(self) -> str:
        return f"<StockNews(symbol={self.symbol}, title={self.title[:50]})>"
    
    @property
    def is_positive_sentiment(self) -> bool:
        """Check if news has positive sentiment."""
        return self.sentiment_score and self.sentiment_score > 0.1
    
    @property
    def is_negative_sentiment(self) -> bool:
        """Check if news has negative sentiment."""
        return self.sentiment_score and self.sentiment_score < -0.1


class MarketSentiment(Base):
    """Market sentiment indicators model."""
    
    __tablename__ = "market_sentiment"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Sentiment data
    fear_greed_index = Column(Numeric(4, 2), nullable=True)  # 0-100
    vix = Column(Numeric(6, 2), nullable=True)  # Volatility index
    put_call_ratio = Column(Numeric(6, 4), nullable=True)
    
    # Market indicators
    advancing_stocks = Column(Integer, nullable=True)
    declining_stocks = Column(Integer, nullable=True)
    unchanged_stocks = Column(Integer, nullable=True)
    
    # Sentiment scores
    overall_sentiment = Column(Numeric(4, 2), nullable=True)  # -1 to 1
    sentiment_label = Column(String(20), nullable=True)  # bullish, bearish, neutral
    
    # Data source
    data_source = Column(String(50), nullable=False)
    
    # Timestamps
    measurement_time = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<MarketSentiment(sentiment={self.sentiment_label}, vix={self.vix})>"


class DataProvider(Base):
    """Data provider configuration model."""
    
    __tablename__ = "data_providers"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Provider information
    name = Column(String(100), unique=True, nullable=False, index=True)
    api_key = Column(String(500), nullable=True)
    base_url = Column(String(500), nullable=False)
    
    # Rate limiting
    requests_per_minute = Column(Integer, default=60, nullable=False)
    requests_per_day = Column(Integer, default=1000, nullable=False)
    current_requests_minute = Column(Integer, default=0, nullable=False)
    current_requests_day = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    priority = Column(Integer, default=1, nullable=False)
    
    # Capabilities
    supports_quotes = Column(Boolean, default=True, nullable=False)
    supports_historical = Column(Boolean, default=True, nullable=False)
    supports_news = Column(Boolean, default=False, nullable=False)
    supports_sentiment = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    last_reset_minute = Column(DateTime, nullable=True)
    last_reset_day = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<DataProvider(name={self.name}, active={self.is_active})>"
    
    @property
    def is_rate_limited(self) -> bool:
        """Check if provider is rate limited."""
        now = datetime.utcnow()
        
        # Check minute limit
        if (self.last_reset_minute and 
            (now - self.last_reset_minute).seconds < 60 and 
            self.current_requests_minute >= self.requests_per_minute):
            return True
        
        # Check day limit
        if (self.last_reset_day and 
            (now - self.last_reset_day).days < 1 and 
            self.current_requests_day >= self.requests_per_day):
            return True
        
        return False

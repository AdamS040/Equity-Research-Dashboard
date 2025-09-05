"""
Pydantic schemas for request/response validation.

Contains Pydantic models for API request/response validation and serialization.
"""

from .auth import (
    TokenData, Token, TokenRefresh, UserBase, UserCreate, UserUpdate,
    UserResponse, UserProfile, UserLogin, UserRegister, PasswordChange,
    PasswordReset, PasswordResetConfirm, EmailVerification, UserSessionResponse,
    UserPreferenceUpdate, UserPreferenceResponse, UserActivityResponse,
    AuthResponse, MessageResponse, ErrorResponse
)
from .market_data import (
    StockBase, StockCreate, StockUpdate, StockResponse,
    StockQuoteBase, StockQuoteCreate, StockQuoteResponse,
    StockHistoricalDataBase, StockHistoricalDataCreate, StockHistoricalDataResponse,
    MarketIndexBase, MarketIndexCreate, MarketIndexResponse,
    SectorBase, SectorCreate, SectorResponse,
    MarketMoverBase, MarketMoverCreate, MarketMoverResponse,
    StockNewsBase, StockNewsCreate, StockNewsResponse,
    MarketSentimentBase, MarketSentimentCreate, MarketSentimentResponse,
    DataProviderBase, DataProviderCreate, DataProviderUpdate, DataProviderResponse,
    MarketOverviewResponse, StockSearchRequest, StockSearchResponse,
    HistoricalDataRequest, HistoricalDataResponse,
    WebSocketMessage, WebSocketSubscription, WebSocketResponse,
    MarketDataError, RateLimitError
)

__all__ = [
    # Auth schemas
    "TokenData", "Token", "TokenRefresh", "UserBase", "UserCreate", "UserUpdate",
    "UserResponse", "UserProfile", "UserLogin", "UserRegister", "PasswordChange",
    "PasswordReset", "PasswordResetConfirm", "EmailVerification", "UserSessionResponse",
    "UserPreferenceUpdate", "UserPreferenceResponse", "UserActivityResponse",
    "AuthResponse", "MessageResponse", "ErrorResponse",
    
    # Market data schemas
    "StockBase", "StockCreate", "StockUpdate", "StockResponse",
    "StockQuoteBase", "StockQuoteCreate", "StockQuoteResponse",
    "StockHistoricalDataBase", "StockHistoricalDataCreate", "StockHistoricalDataResponse",
    "MarketIndexBase", "MarketIndexCreate", "MarketIndexResponse",
    "SectorBase", "SectorCreate", "SectorResponse",
    "MarketMoverBase", "MarketMoverCreate", "MarketMoverResponse",
    "StockNewsBase", "StockNewsCreate", "StockNewsResponse",
    "MarketSentimentBase", "MarketSentimentCreate", "MarketSentimentResponse",
    "DataProviderBase", "DataProviderCreate", "DataProviderUpdate", "DataProviderResponse",
    "MarketOverviewResponse", "StockSearchRequest", "StockSearchResponse",
    "HistoricalDataRequest", "HistoricalDataResponse",
    "WebSocketMessage", "WebSocketSubscription", "WebSocketResponse",
    "MarketDataError", "RateLimitError"
]
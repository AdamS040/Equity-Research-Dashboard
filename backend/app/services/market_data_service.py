"""
Market data service for financial data integration.

Handles integration with multiple financial data providers with fallback strategies.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

import httpx
import yfinance as yf
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert

from app.config import settings
from app.models.market_data import (
    Stock, StockQuote, StockHistoricalData, MarketIndex, Sector,
    MarketMover, StockNews, MarketSentiment, DataProvider
)
from app.schemas.market_data import (
    StockCreate, StockQuoteCreate, StockHistoricalDataCreate,
    MarketIndexCreate, SectorCreate, MarketMoverCreate,
    StockNewsCreate, MarketSentimentCreate
)
from app.utils.logging import get_logger
from app.utils.redis_client import redis_manager

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, requests_per_minute: int, requests_per_day: int):
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        self.minute_requests = 0
        self.day_requests = 0
        self.last_minute_reset = datetime.utcnow()
        self.last_day_reset = datetime.utcnow()
    
    async def can_make_request(self) -> bool:
        """Check if we can make a request without exceeding rate limits."""
        now = datetime.utcnow()
        
        # Reset minute counter if needed
        if (now - self.last_minute_reset).seconds >= 60:
            self.minute_requests = 0
            self.last_minute_reset = now
        
        # Reset day counter if needed
        if (now - self.last_day_reset).days >= 1:
            self.day_requests = 0
            self.last_day_reset = now
        
        return (self.minute_requests < self.requests_per_minute and 
                self.day_requests < self.requests_per_day)
    
    async def record_request(self):
        """Record a request."""
        self.minute_requests += 1
        self.day_requests += 1


class FinancialModelingPrepClient:
    """Financial Modeling Prep API client."""
    
    def __init__(self):
        self.api_key = settings.financial_modeling_prep_api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.timeout = 30.0
        self.rate_limiter = RateLimiter(250, 10000)  # FMP limits
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote."""
        if not self.api_key:
            logger.warning("Financial Modeling Prep API key not configured")
            return None
        
        if not await self.rate_limiter.can_make_request():
            logger.warning(f"FMP rate limit exceeded for {symbol}")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/quote/{symbol}",
                    params={"apikey": self.api_key}
                )
                response.raise_for_status()
                data = response.json()
                await self.rate_limiter.record_request()
                return data[0] if data else None
        except Exception as e:
            logger.error(f"FMP quote request failed for {symbol}: {e}")
            return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1y"
    ) -> Optional[List[Dict[str, Any]]]:
        """Get historical price data."""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/historical-price-full/{symbol}",
                    params={
                        "apikey": self.api_key,
                        "timeseries": period
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("historical", [])
        except Exception as e:
            logger.error(f"FMP historical data request failed for {symbol}: {e}")
            return None
    
    async def get_financial_statements(
        self, 
        symbol: str, 
        statement_type: str = "income-statement"
    ) -> Optional[List[Dict[str, Any]]]:
        """Get financial statements."""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/{statement_type}/{symbol}",
                    params={"apikey": self.api_key}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"FMP financial statements request failed for {symbol}: {e}")
            return None
    
    async def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company profile information."""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/profile/{symbol}",
                    params={"apikey": self.api_key}
                )
                response.raise_for_status()
                data = response.json()
                return data[0] if data else None
        except Exception as e:
            logger.error(f"FMP company profile request failed for {symbol}: {e}")
            return None


class YahooFinanceClient:
    """Yahoo Finance client using yfinance library."""
    
    def __init__(self):
        self.timeout = 30.0
        self.rate_limiter = RateLimiter(2000, 100000)  # Yahoo Finance limits
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote."""
        if not await self.rate_limiter.can_make_request():
            logger.warning(f"Yahoo Finance rate limit exceeded for {symbol}")
            return None
        
        try:
            # Run yfinance in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, ticker.info)
            history = await loop.run_in_executor(
                None, 
                lambda: ticker.history(period="1d", interval="1m")
            )
            
            if info and not history.empty:
                latest = history.iloc[-1]
                await self.rate_limiter.record_request()
                
                return {
                    "symbol": symbol,
                    "price": float(latest["Close"]),
                    "change": float(latest["Close"] - latest["Open"]),
                    "changePercent": float((latest["Close"] - latest["Open"]) / latest["Open"] * 100),
                    "volume": int(latest["Volume"]),
                    "high": float(latest["High"]),
                    "low": float(latest["Low"]),
                    "open": float(latest["Open"]),
                    "previousClose": float(info.get("previousClose", latest["Open"])),
                    "marketCap": info.get("marketCap"),
                    "peRatio": info.get("trailingPE"),
                    "eps": info.get("trailingEps"),
                    "dividendYield": info.get("dividendYield"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"Yahoo Finance quote request failed for {symbol}: {e}")
            return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[List[Dict[str, Any]]]:
        """Get historical price data."""
        if not await self.rate_limiter.can_make_request():
            logger.warning(f"Yahoo Finance rate limit exceeded for {symbol}")
            return None
        
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            history = await loop.run_in_executor(
                None, 
                lambda: ticker.history(period=period, interval=interval)
            )
            
            if not history.empty:
                await self.rate_limiter.record_request()
                
                data = []
                for date, row in history.iterrows():
                    data.append({
                        "date": date.isoformat(),
                        "open": float(row["Open"]),
                        "high": float(row["High"]),
                        "low": float(row["Low"]),
                        "close": float(row["Close"]),
                        "volume": int(row["Volume"]),
                        "adjusted_close": float(row["Close"])  # Simplified
                    })
                return data
            return None
        except Exception as e:
            logger.error(f"Yahoo Finance historical data request failed for {symbol}: {e}")
            return None
    
    async def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company profile information."""
        if not await self.rate_limiter.can_make_request():
            logger.warning(f"Yahoo Finance rate limit exceeded for {symbol}")
            return None
        
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, ticker.info)
            
            if info:
                await self.rate_limiter.record_request()
                
                return {
                    "symbol": symbol,
                    "name": info.get("longName", info.get("shortName", symbol)),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "marketCap": info.get("marketCap"),
                    "description": info.get("longBusinessSummary"),
                    "website": info.get("website"),
                    "logo_url": info.get("logo_url"),
                    "exchange": info.get("exchange"),
                    "currency": info.get("currency", "USD")
                }
            return None
        except Exception as e:
            logger.error(f"Yahoo Finance company profile request failed for {symbol}: {e}")
            return None


class AlphaVantageClient:
    """Alpha Vantage API client."""
    
    def __init__(self):
        self.api_key = settings.alpha_vantage_api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.timeout = 30.0
        self.rate_limiter = RateLimiter(5, 500)  # Alpha Vantage limits
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote."""
        if not self.api_key:
            logger.warning("Alpha Vantage API key not configured")
            return None
        
        if not await self.rate_limiter.can_make_request():
            logger.warning(f"Alpha Vantage rate limit exceeded for {symbol}")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "function": "GLOBAL_QUOTE",
                        "symbol": symbol,
                        "apikey": self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Check for API error messages
                if "Error Message" in data:
                    logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                    return None
                
                if "Note" in data:
                    logger.warning(f"Alpha Vantage API note: {data['Note']}")
                    return None
                
                # Alpha Vantage returns data in a different format
                quote_data = data.get("Global Quote", {})
                if not quote_data:
                    return None
                
                await self.rate_limiter.record_request()
                
                # Transform to standard format
                return {
                    "symbol": quote_data.get("01. symbol"),
                    "price": float(quote_data.get("05. price", 0)),
                    "change": float(quote_data.get("09. change", 0)),
                    "changePercent": float(quote_data.get("10. change percent", "0%").replace("%", "")),
                    "volume": int(quote_data.get("06. volume", 0)),
                    "high": float(quote_data.get("03. high", 0)),
                    "low": float(quote_data.get("04. low", 0)),
                    "open": float(quote_data.get("02. open", 0)),
                    "previousClose": float(quote_data.get("08. previous close", 0)),
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Alpha Vantage quote request failed for {symbol}: {e}")
            return None
    
    async def get_technical_indicator(
        self, 
        symbol: str, 
        indicator: str = "RSI"
    ) -> Optional[Dict[str, Any]]:
        """Get technical indicators."""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "function": indicator,
                        "symbol": symbol,
                        "interval": "daily",
                        "time_period": 14,
                        "series_type": "close",
                        "apikey": self.api_key
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Alpha Vantage technical indicator request failed for {symbol}: {e}")
            return None


class TiingoClient:
    """Tiingo API client."""
    
    def __init__(self):
        self.api_key = settings.tiingo_api_key
        self.base_url = "https://api.tiingo.com"
        self.timeout = 30.0
        self.rate_limiter = RateLimiter(1000, 50000)  # Tiingo limits
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote."""
        if not self.api_key:
            logger.warning("Tiingo API key not configured")
            return None
        
        if not await self.rate_limiter.can_make_request():
            logger.warning(f"Tiingo rate limit exceeded for {symbol}")
            return None
        
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/iex/{symbol}",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                await self.rate_limiter.record_request()
                return data[0] if data else None
        except Exception as e:
            logger.error(f"Tiingo quote request failed for {symbol}: {e}")
            return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Get historical price data."""
        if not self.api_key:
            return None
        
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/tiingo/daily/{symbol}/prices",
                    headers=headers,
                    params={
                        "startDate": start_date,
                        "endDate": end_date
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Tiingo historical data request failed for {symbol}: {e}")
            return None


class MarketDataService:
    """Main market data service with fallback strategy."""
    
    def __init__(self):
        self.fmp_client = FinancialModelingPrepClient()
        self.yahoo_client = YahooFinanceClient()
        self.alpha_vantage_client = AlphaVantageClient()
        self.tiingo_client = TiingoClient()
        
        # Provider priority order (first is primary)
        self.providers = [
            ("yahoo", self.yahoo_client),
            ("fmp", self.fmp_client),
            ("alpha_vantage", self.alpha_vantage_client),
            ("tiingo", self.tiingo_client)
        ]
    
    async def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get stock quote with fallback strategy.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Stock quote data or None if all sources fail
        """
        # Try providers in priority order
        for provider_name, client in self.providers:
            try:
                quote = await client.get_quote(symbol)
                if quote:
                    logger.info(f"Got quote for {symbol} from {provider_name}")
                    # Add provider info to quote
                    quote["data_source"] = provider_name
                    return quote
            except Exception as e:
                logger.warning(f"{provider_name} failed for {symbol}: {e}")
                continue
        
        logger.error(f"All data sources failed for {symbol}")
        return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get historical data with fallback strategy.
        
        Args:
            symbol: Stock symbol
            period: Time period (1y, 5y, etc.)
            interval: Data interval (1d, 1h, etc.)
            
        Returns:
            Historical data or None if all sources fail
        """
        # Try providers in priority order
        for provider_name, client in self.providers:
            try:
                if provider_name == "yahoo":
                    data = await client.get_historical_data(symbol, period, interval)
                elif provider_name == "fmp":
                    data = await client.get_historical_data(symbol, period)
                elif provider_name == "tiingo":
                    end_date = datetime.now().strftime("%Y-%m-%d")
                    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                    data = await client.get_historical_data(symbol, start_date, end_date)
                else:
                    continue
                
                if data:
                    logger.info(f"Got historical data for {symbol} from {provider_name}")
                    return data
            except Exception as e:
                logger.warning(f"{provider_name} historical data failed for {symbol}: {e}")
                continue
        
        logger.error(f"All historical data sources failed for {symbol}")
        return None
    
    async def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get company profile information.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Company profile data or None if all sources fail
        """
        # Try providers in priority order
        for provider_name, client in self.providers:
            try:
                if provider_name in ["yahoo", "fmp"]:
                    profile = await client.get_company_profile(symbol)
                    if profile:
                        logger.info(f"Got company profile for {symbol} from {provider_name}")
                        profile["data_source"] = provider_name
                        return profile
            except Exception as e:
                logger.warning(f"{provider_name} company profile failed for {symbol}: {e}")
                continue
        
        logger.error(f"All company profile sources failed for {symbol}")
        return None
    
    async def get_financial_statements(
        self, 
        symbol: str, 
        statement_type: str = "income-statement"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get financial statements.
        
        Args:
            symbol: Stock symbol
            statement_type: Type of financial statement
            
        Returns:
            Financial statements data or None if all sources fail
        """
        # Try FMP first
        try:
            statements = await self.fmp_client.get_financial_statements(symbol, statement_type)
            if statements:
                logger.info(f"Got financial statements for {symbol} from FMP")
                return statements
        except Exception as e:
            logger.warning(f"FMP financial statements failed for {symbol}: {e}")
        
        logger.error(f"All financial statements sources failed for {symbol}")
        return None
    
    async def get_technical_indicators(
        self, 
        symbol: str, 
        indicator: str = "RSI"
    ) -> Optional[Dict[str, Any]]:
        """
        Get technical indicators.
        
        Args:
            symbol: Stock symbol
            indicator: Technical indicator type
            
        Returns:
            Technical indicator data or None if all sources fail
        """
        # Try Alpha Vantage first (best for technical indicators)
        try:
            indicators = await self.alpha_vantage_client.get_technical_indicator(symbol, indicator)
            if indicators:
                logger.info(f"Got technical indicators for {symbol} from Alpha Vantage")
                return indicators
        except Exception as e:
            logger.warning(f"Alpha Vantage technical indicators failed for {symbol}: {e}")
        
        logger.error(f"All technical indicators sources failed for {symbol}")
        return None
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Get quotes for multiple symbols concurrently.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbols to quote data
        """
        tasks = [self.get_stock_quote(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            symbol: result if not isinstance(result, Exception) else None
            for symbol, result in zip(symbols, results)
        }
    
    async def get_market_indices(self) -> List[Dict[str, Any]]:
        """Get major market indices."""
        indices = []
        index_symbols = ["^GSPC", "^IXIC", "^DJI", "^VIX"]  # S&P 500, NASDAQ, DOW, VIX
        
        for symbol in index_symbols:
            try:
                quote = await self.yahoo_client.get_quote(symbol)
                if quote:
                    indices.append({
                        "symbol": symbol,
                        "name": self._get_index_name(symbol),
                        "value": quote["price"],
                        "change": quote["change"],
                        "change_percent": quote["changePercent"],
                        "data_source": "yahoo"
                    })
            except Exception as e:
                logger.warning(f"Failed to get index {symbol}: {e}")
        
        return indices
    
    def _get_index_name(self, symbol: str) -> str:
        """Get index name from symbol."""
        names = {
            "^GSPC": "S&P 500",
            "^IXIC": "NASDAQ Composite",
            "^DJI": "Dow Jones Industrial Average",
            "^VIX": "CBOE Volatility Index"
        }
        return names.get(symbol, symbol)
    
    async def get_market_movers(self, mover_type: str = "gainers") -> List[Dict[str, Any]]:
        """Get market movers (gainers, losers, most active)."""
        # This would typically come from a market data provider
        # For now, return mock data or implement with available providers
        return []
    
    async def get_sector_performance(self) -> List[Dict[str, Any]]:
        """Get sector performance data."""
        # This would typically come from a market data provider
        # For now, return mock data or implement with available providers
        return []
    
    async def get_market_sentiment(self) -> Optional[Dict[str, Any]]:
        """Get market sentiment indicators."""
        try:
            # Get VIX as a sentiment indicator
            vix_quote = await self.yahoo_client.get_quote("^VIX")
            if vix_quote:
                vix_value = vix_quote["price"]
                
                # Simple sentiment calculation based on VIX
                if vix_value < 20:
                    sentiment = "bullish"
                    sentiment_score = 0.7
                elif vix_value > 30:
                    sentiment = "bearish"
                    sentiment_score = -0.7
                else:
                    sentiment = "neutral"
                    sentiment_score = 0.0
                
                return {
                    "vix": vix_value,
                    "sentiment": sentiment,
                    "sentiment_score": sentiment_score,
                    "data_source": "yahoo"
                }
        except Exception as e:
            logger.error(f"Failed to get market sentiment: {e}")
        
        return None
    
    async def search_stocks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for stocks by symbol or name."""
        # This would typically use a search API or database
        # For now, return mock data
        return []
    
    def get_available_providers(self) -> List[str]:
        """Get list of available data providers."""
        providers = []
        
        # Yahoo Finance is always available
        providers.append("Yahoo Finance")
        
        if self.fmp_client.api_key:
            providers.append("Financial Modeling Prep")
        
        if self.alpha_vantage_client.api_key:
            providers.append("Alpha Vantage")
        
        if self.tiingo_client.api_key:
            providers.append("Tiingo")
        
        return providers


# Global market data service instance
market_data_service = MarketDataService()

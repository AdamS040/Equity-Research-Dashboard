"""
Cache service for market data.

Handles Redis caching with invalidation strategies and data preprocessing.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.market_data import (
    Stock, StockQuote, StockHistoricalData, MarketIndex, Sector,
    MarketMover, StockNews, MarketSentiment
)
from app.schemas.market_data import (
    StockResponse, StockQuoteResponse, StockHistoricalDataResponse,
    MarketIndexResponse, SectorResponse, MarketMoverResponse,
    StockNewsResponse, MarketSentimentResponse
)
from app.utils.logging import get_logger
from app.utils.redis_client import redis_manager

logger = get_logger(__name__)


class CacheService:
    """Service for caching market data with Redis."""
    
    def __init__(self):
        self.default_ttl = 300  # 5 minutes default TTL
        self.quote_ttl = 60     # 1 minute for quotes
        self.historical_ttl = 3600  # 1 hour for historical data
        self.profile_ttl = 1800     # 30 minutes for company profiles
        self.news_ttl = 900         # 15 minutes for news
        self.indices_ttl = 120      # 2 minutes for indices
        self.sentiment_ttl = 300    # 5 minutes for sentiment
    
    async def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached stock quote."""
        cache_key = f"quote:{symbol.upper()}"
        try:
            cached_data = await redis_manager.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting cached quote for {symbol}: {e}")
        return None
    
    async def set_stock_quote(self, symbol: str, quote_data: Dict[str, Any], ttl: Optional[int] = None):
        """Cache stock quote."""
        cache_key = f"quote:{symbol.upper()}"
        ttl = ttl or self.quote_ttl
        try:
            await redis_manager.set(cache_key, json.dumps(quote_data, default=str), expire=ttl)
        except Exception as e:
            logger.error(f"Error caching quote for {symbol}: {e}")
    
    async def get_historical_data(self, symbol: str, period: str, interval: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached historical data."""
        cache_key = f"historical:{symbol.upper()}:{period}:{interval}"
        try:
            cached_data = await redis_manager.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting cached historical data for {symbol}: {e}")
        return None
    
    async def set_historical_data(self, symbol: str, period: str, interval: str, data: List[Dict[str, Any]], ttl: Optional[int] = None):
        """Cache historical data."""
        cache_key = f"historical:{symbol.upper()}:{period}:{interval}"
        ttl = ttl or self.historical_ttl
        try:
            await redis_manager.set(cache_key, json.dumps(data, default=str), expire=ttl)
        except Exception as e:
            logger.error(f"Error caching historical data for {symbol}: {e}")
    
    async def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached company profile."""
        cache_key = f"profile:{symbol.upper()}"
        try:
            cached_data = await redis_manager.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting cached profile for {symbol}: {e}")
        return None
    
    async def set_company_profile(self, symbol: str, profile_data: Dict[str, Any], ttl: Optional[int] = None):
        """Cache company profile."""
        cache_key = f"profile:{symbol.upper()}"
        ttl = ttl or self.profile_ttl
        try:
            await redis_manager.set(cache_key, json.dumps(profile_data, default=str), expire=ttl)
        except Exception as e:
            logger.error(f"Error caching profile for {symbol}: {e}")
    
    async def get_market_indices(self) -> Optional[List[Dict[str, Any]]]:
        """Get cached market indices."""
        cache_key = "market:indices"
        try:
            cached_data = await redis_manager.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting cached market indices: {e}")
        return None
    
    async def set_market_indices(self, indices_data: List[Dict[str, Any]], ttl: Optional[int] = None):
        """Cache market indices."""
        cache_key = "market:indices"
        ttl = ttl or self.indices_ttl
        try:
            await redis_manager.set(cache_key, json.dumps(indices_data, default=str), expire=ttl)
        except Exception as e:
            logger.error(f"Error caching market indices: {e}")
    
    async def get_market_sentiment(self) -> Optional[Dict[str, Any]]:
        """Get cached market sentiment."""
        cache_key = "market:sentiment"
        try:
            cached_data = await redis_manager.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting cached market sentiment: {e}")
        return None
    
    async def set_market_sentiment(self, sentiment_data: Dict[str, Any], ttl: Optional[int] = None):
        """Cache market sentiment."""
        cache_key = "market:sentiment"
        ttl = ttl or self.sentiment_ttl
        try:
            await redis_manager.set(cache_key, json.dumps(sentiment_data, default=str), expire=ttl)
        except Exception as e:
            logger.error(f"Error caching market sentiment: {e}")
    
    async def get_sector_performance(self) -> Optional[List[Dict[str, Any]]]:
        """Get cached sector performance."""
        cache_key = "market:sectors"
        try:
            cached_data = await redis_manager.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting cached sector performance: {e}")
        return None
    
    async def set_sector_performance(self, sectors_data: List[Dict[str, Any]], ttl: Optional[int] = None):
        """Cache sector performance."""
        cache_key = "market:sectors"
        ttl = ttl or self.default_ttl
        try:
            await redis_manager.set(cache_key, json.dumps(sectors_data, default=str), expire=ttl)
        except Exception as e:
            logger.error(f"Error caching sector performance: {e}")
    
    async def get_market_movers(self, mover_type: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached market movers."""
        cache_key = f"market:movers:{mover_type}"
        try:
            cached_data = await redis_manager.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting cached market movers: {e}")
        return None
    
    async def set_market_movers(self, mover_type: str, movers_data: List[Dict[str, Any]], ttl: Optional[int] = None):
        """Cache market movers."""
        cache_key = f"market:movers:{mover_type}"
        ttl = ttl or self.default_ttl
        try:
            await redis_manager.set(cache_key, json.dumps(movers_data, default=str), expire=ttl)
        except Exception as e:
            logger.error(f"Error caching market movers: {e}")
    
    async def get_stock_news(self, symbol: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get cached stock news."""
        cache_key = f"news:{symbol.upper()}:{limit}"
        try:
            cached_data = await redis_manager.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting cached news for {symbol}: {e}")
        return None
    
    async def set_stock_news(self, symbol: str, news_data: List[Dict[str, Any]], limit: int = 10, ttl: Optional[int] = None):
        """Cache stock news."""
        cache_key = f"news:{symbol.upper()}:{limit}"
        ttl = ttl or self.news_ttl
        try:
            await redis_manager.set(cache_key, json.dumps(news_data, default=str), expire=ttl)
        except Exception as e:
            logger.error(f"Error caching news for {symbol}: {e}")
    
    async def get_stock_search(self, query: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get cached stock search results."""
        cache_key = f"search:{query.lower()}:{limit}"
        try:
            cached_data = await redis_manager.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting cached search results: {e}")
        return None
    
    async def set_stock_search(self, query: str, search_data: List[Dict[str, Any]], limit: int = 10, ttl: Optional[int] = None):
        """Cache stock search results."""
        cache_key = f"search:{query.lower()}:{limit}"
        ttl = ttl or self.default_ttl
        try:
            await redis_manager.set(cache_key, json.dumps(search_data, default=str), expire=ttl)
        except Exception as e:
            logger.error(f"Error caching search results: {e}")
    
    async def invalidate_stock_data(self, symbol: str):
        """Invalidate all cached data for a stock."""
        symbol_upper = symbol.upper()
        patterns = [
            f"quote:{symbol_upper}",
            f"profile:{symbol_upper}",
            f"historical:{symbol_upper}:*",
            f"news:{symbol_upper}:*"
        ]
        
        for pattern in patterns:
            try:
                await redis_manager.delete(pattern)
            except Exception as e:
                logger.error(f"Error invalidating cache for {pattern}: {e}")
    
    async def invalidate_market_data(self):
        """Invalidate all market data cache."""
        patterns = [
            "market:indices",
            "market:sentiment",
            "market:sectors",
            "market:movers:*"
        ]
        
        for pattern in patterns:
            try:
                await redis_manager.delete(pattern)
            except Exception as e:
                logger.error(f"Error invalidating market cache for {pattern}: {e}")
    
    async def warm_cache(self, symbols: List[str]):
        """Warm the cache with frequently accessed data."""
        logger.info(f"Warming cache for {len(symbols)} symbols")
        
        # Import here to avoid circular imports
        from app.services.market_data_service import market_data_service
        
        tasks = []
        for symbol in symbols:
            # Warm quote cache
            tasks.append(self._warm_quote_cache(symbol))
            # Warm profile cache
            tasks.append(self._warm_profile_cache(symbol))
        
        # Warm market data cache
        tasks.append(self._warm_market_cache())
        
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Cache warming completed")
    
    async def _warm_quote_cache(self, symbol: str):
        """Warm quote cache for a symbol."""
        try:
            from app.services.market_data_service import market_data_service
            quote = await market_data_service.get_stock_quote(symbol)
            if quote:
                await self.set_stock_quote(symbol, quote)
        except Exception as e:
            logger.error(f"Error warming quote cache for {symbol}: {e}")
    
    async def _warm_profile_cache(self, symbol: str):
        """Warm profile cache for a symbol."""
        try:
            from app.services.market_data_service import market_data_service
            profile = await market_data_service.get_company_profile(symbol)
            if profile:
                await self.set_company_profile(symbol, profile)
        except Exception as e:
            logger.error(f"Error warming profile cache for {symbol}: {e}")
    
    async def _warm_market_cache(self):
        """Warm market data cache."""
        try:
            from app.services.market_data_service import market_data_service
            
            # Warm indices cache
            indices = await market_data_service.get_market_indices()
            if indices:
                await self.set_market_indices(indices)
            
            # Warm sentiment cache
            sentiment = await market_data_service.get_market_sentiment()
            if sentiment:
                await self.set_market_sentiment(sentiment)
            
        except Exception as e:
            logger.error(f"Error warming market cache: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            # Get Redis info
            redis_info = await redis_manager.get_redis_info()
            
            # Count keys by pattern
            patterns = [
                "quote:*",
                "profile:*",
                "historical:*",
                "news:*",
                "market:*",
                "search:*"
            ]
            
            key_counts = {}
            for pattern in patterns:
                try:
                    keys = await redis_manager.get_keys(pattern)
                    key_counts[pattern] = len(keys)
                except Exception as e:
                    logger.error(f"Error counting keys for {pattern}: {e}")
                    key_counts[pattern] = 0
            
            return {
                "redis_info": redis_info,
                "key_counts": key_counts,
                "cache_ttl": {
                    "quote": self.quote_ttl,
                    "historical": self.historical_ttl,
                    "profile": self.profile_ttl,
                    "news": self.news_ttl,
                    "indices": self.indices_ttl,
                    "sentiment": self.sentiment_ttl,
                    "default": self.default_ttl
                }
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}


# Global cache service instance
cache_service = CacheService()

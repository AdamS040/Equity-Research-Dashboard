"""
Market data service for financial data integration.

Handles integration with multiple financial data providers as alternatives to IEX Cloud.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class FinancialModelingPrepClient:
    """Financial Modeling Prep API client."""
    
    def __init__(self):
        self.api_key = settings.financial_modeling_prep_api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.timeout = 30.0
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote."""
        if not self.api_key:
            logger.warning("Financial Modeling Prep API key not configured")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/quote/{symbol}",
                    params={"apikey": self.api_key}
                )
                response.raise_for_status()
                data = response.json()
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


class AlphaVantageClient:
    """Alpha Vantage API client."""
    
    def __init__(self):
        self.api_key = settings.alpha_vantage_api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.timeout = 30.0
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote."""
        if not self.api_key:
            logger.warning("Alpha Vantage API key not configured")
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
                
                # Alpha Vantage returns data in a different format
                quote_data = data.get("Global Quote", {})
                if not quote_data:
                    return None
                
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
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote."""
        if not self.api_key:
            logger.warning("Tiingo API key not configured")
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
        self.alpha_vantage_client = AlphaVantageClient()
        self.tiingo_client = TiingoClient()
    
    async def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get stock quote with fallback strategy.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Stock quote data or None if all sources fail
        """
        # Try FMP first (primary)
        try:
            quote = await self.fmp_client.get_quote(symbol)
            if quote:
                logger.info(f"Got quote for {symbol} from FMP")
                return quote
        except Exception as e:
            logger.warning(f"FMP failed for {symbol}: {e}")
        
        # Fallback to Alpha Vantage
        try:
            quote = await self.alpha_vantage_client.get_quote(symbol)
            if quote:
                logger.info(f"Got quote for {symbol} from Alpha Vantage")
                return quote
        except Exception as e:
            logger.warning(f"Alpha Vantage failed for {symbol}: {e}")
        
        # Final fallback to Tiingo
        try:
            quote = await self.tiingo_client.get_quote(symbol)
            if quote:
                logger.info(f"Got quote for {symbol} from Tiingo")
                return quote
        except Exception as e:
            logger.warning(f"Tiingo failed for {symbol}: {e}")
        
        logger.error(f"All data sources failed for {symbol}")
        return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1y"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get historical data with fallback strategy.
        
        Args:
            symbol: Stock symbol
            period: Time period (1y, 5y, etc.)
            
        Returns:
            Historical data or None if all sources fail
        """
        # Try FMP first
        try:
            data = await self.fmp_client.get_historical_data(symbol, period)
            if data:
                logger.info(f"Got historical data for {symbol} from FMP")
                return data
        except Exception as e:
            logger.warning(f"FMP historical data failed for {symbol}: {e}")
        
        # Fallback to Tiingo
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            data = await self.tiingo_client.get_historical_data(symbol, start_date, end_date)
            if data:
                logger.info(f"Got historical data for {symbol} from Tiingo")
                return data
        except Exception as e:
            logger.warning(f"Tiingo historical data failed for {symbol}: {e}")
        
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
        # Try FMP first
        try:
            profile = await self.fmp_client.get_company_profile(symbol)
            if profile:
                logger.info(f"Got company profile for {symbol} from FMP")
                return profile
        except Exception as e:
            logger.warning(f"FMP company profile failed for {symbol}: {e}")
        
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
    
    def get_available_providers(self) -> List[str]:
        """Get list of available data providers."""
        providers = []
        
        if self.fmp_client.api_key:
            providers.append("Financial Modeling Prep")
        
        if self.alpha_vantage_client.api_key:
            providers.append("Alpha Vantage")
        
        if self.tiingo_client.api_key:
            providers.append("Tiingo")
        
        return providers


# Global market data service instance
market_data_service = MarketDataService()

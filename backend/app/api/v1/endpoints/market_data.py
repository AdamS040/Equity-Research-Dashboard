"""
Market data endpoints.

Handles market data requests with multiple provider fallback.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.services.market_data_service import market_data_service
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/quote/{symbol}")
async def get_stock_quote(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get real-time stock quote.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, MSFT)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Stock quote data
    """
    try:
        quote = await market_data_service.get_stock_quote(symbol.upper())
        
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote not found for symbol {symbol}"
            )
        
        logger.info(f"Quote retrieved for {symbol} by user {current_user.id}")
        return {
            "symbol": symbol.upper(),
            "data": quote,
            "provider": "Multiple providers with fallback",
            "timestamp": quote.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Error getting quote for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stock quote"
        )


@router.get("/quotes")
async def get_multiple_quotes(
    symbols: List[str] = Query(..., description="List of stock symbols"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get quotes for multiple symbols.
    
    Args:
        symbols: List of stock symbols
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dictionary of quotes by symbol
    """
    try:
        # Limit to 10 symbols to prevent abuse
        if len(symbols) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 symbols allowed per request"
            )
        
        # Convert to uppercase
        symbols_upper = [symbol.upper() for symbol in symbols]
        
        quotes = await market_data_service.get_multiple_quotes(symbols_upper)
        
        logger.info(f"Multiple quotes retrieved for {len(symbols)} symbols by user {current_user.id}")
        return {
            "symbols": symbols_upper,
            "quotes": quotes,
            "provider": "Multiple providers with fallback",
            "timestamp": quotes.get("timestamp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting multiple quotes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stock quotes"
        )


@router.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = Query("1y", description="Time period (1y, 5y, etc.)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical price data.
    
    Args:
        symbol: Stock symbol
        period: Time period
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Historical price data
    """
    try:
        historical_data = await market_data_service.get_historical_data(
            symbol.upper(), 
            period
        )
        
        if not historical_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Historical data not found for symbol {symbol}"
            )
        
        logger.info(f"Historical data retrieved for {symbol} by user {current_user.id}")
        return {
            "symbol": symbol.upper(),
            "period": period,
            "data": historical_data,
            "provider": "Multiple providers with fallback",
            "count": len(historical_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting historical data for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve historical data"
        )


@router.get("/profile/{symbol}")
async def get_company_profile(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get company profile information.
    
    Args:
        symbol: Stock symbol
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Company profile data
    """
    try:
        profile = await market_data_service.get_company_profile(symbol.upper())
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company profile not found for symbol {symbol}"
            )
        
        logger.info(f"Company profile retrieved for {symbol} by user {current_user.id}")
        return {
            "symbol": symbol.upper(),
            "profile": profile,
            "provider": "Multiple providers with fallback"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company profile for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company profile"
        )


@router.get("/technical/{symbol}")
async def get_technical_indicators(
    symbol: str,
    indicator: str = Query("RSI", description="Technical indicator type"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get technical indicators.
    
    Args:
        symbol: Stock symbol
        indicator: Technical indicator type (RSI, MACD, etc.)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Technical indicator data
    """
    try:
        indicators = await market_data_service.get_technical_indicators(
            symbol.upper(), 
            indicator
        )
        
        if not indicators:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Technical indicators not found for symbol {symbol}"
            )
        
        logger.info(f"Technical indicators retrieved for {symbol} by user {current_user.id}")
        return {
            "symbol": symbol.upper(),
            "indicator": indicator,
            "data": indicators,
            "provider": "Multiple providers with fallback"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting technical indicators for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve technical indicators"
        )


@router.get("/providers")
async def get_available_providers(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available data providers.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of available providers
    """
    try:
        providers = market_data_service.get_available_providers()
        
        return {
            "available_providers": providers,
            "total_providers": len(providers),
            "fallback_strategy": "Primary: Financial Modeling Prep, Secondary: Alpha Vantage, Tertiary: Tiingo"
        }
        
    except Exception as e:
        logger.error(f"Error getting available providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve provider information"
        )

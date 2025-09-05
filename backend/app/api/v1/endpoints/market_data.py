"""
Market data endpoints.

Handles market data requests with multiple provider fallback and caching.
"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.services.market_data_service import market_data_service
from app.services.cache_service import cache_service
from app.services.websocket_service import websocket_service
from app.services.background_jobs import get_task_status, get_active_tasks
from app.schemas.market_data import (
    StockSearchRequest, StockSearchResponse, HistoricalDataRequest, HistoricalDataResponse,
    MarketOverviewResponse, WebSocketSubscription, WebSocketResponse
)
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
    Get real-time stock quote with caching.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, MSFT)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Stock quote data
    """
    try:
        symbol_upper = symbol.upper()
        
        # Try cache first
        cached_quote = await cache_service.get_stock_quote(symbol_upper)
        if cached_quote:
            logger.info(f"Cached quote retrieved for {symbol_upper} by user {current_user.id}")
            return {
                "symbol": symbol_upper,
                "data": cached_quote,
                "cached": True,
                "timestamp": cached_quote.get("timestamp")
            }
        
        # Get fresh data
        quote = await market_data_service.get_stock_quote(symbol_upper)
        
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote not found for symbol {symbol}"
            )
        
        # Cache the quote
        await cache_service.set_stock_quote(symbol_upper, quote)
        
        logger.info(f"Fresh quote retrieved for {symbol_upper} by user {current_user.id}")
        return {
            "symbol": symbol_upper,
            "data": quote,
            "cached": False,
            "provider": quote.get("data_source", "unknown"),
            "timestamp": quote.get("timestamp")
        }
        
    except HTTPException:
        raise
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


@router.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get market overview with indices, movers, and sentiment.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Market overview data
    """
    try:
        # Try cache first
        cached_indices = await cache_service.get_market_indices()
        cached_sentiment = await cache_service.get_market_sentiment()
        cached_gainers = await cache_service.get_market_movers("gainers")
        cached_losers = await cache_service.get_market_movers("losers")
        cached_active = await cache_service.get_market_movers("active")
        
        # Get fresh data if not cached
        if not cached_indices:
            cached_indices = await market_data_service.get_market_indices()
            if cached_indices:
                await cache_service.set_market_indices(cached_indices)
        
        if not cached_sentiment:
            cached_sentiment = await market_data_service.get_market_sentiment()
            if cached_sentiment:
                await cache_service.set_market_sentiment(cached_sentiment)
        
        if not cached_gainers:
            cached_gainers = await market_data_service.get_market_movers("gainers")
            if cached_gainers:
                await cache_service.set_market_movers("gainers", cached_gainers)
        
        if not cached_losers:
            cached_losers = await market_data_service.get_market_movers("losers")
            if cached_losers:
                await cache_service.set_market_movers("losers", cached_losers)
        
        if not cached_active:
            cached_active = await market_data_service.get_market_movers("active")
            if cached_active:
                await cache_service.set_market_movers("active", cached_active)
        
        logger.info(f"Market overview retrieved by user {current_user.id}")
        
        return MarketOverviewResponse(
            market_status="open",  # This would be determined by market hours
            market_indices=cached_indices or [],
            top_gainers=cached_gainers or [],
            top_losers=cached_losers or [],
            most_active=cached_active or [],
            market_sentiment=cached_sentiment,
            last_update=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve market overview"
        )


@router.get("/indices")
async def get_market_indices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get major market indices.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Market indices data
    """
    try:
        # Try cache first
        cached_indices = await cache_service.get_market_indices()
        if cached_indices:
            logger.info(f"Cached market indices retrieved by user {current_user.id}")
            return {
                "indices": cached_indices,
                "cached": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get fresh data
        indices = await market_data_service.get_market_indices()
        if indices:
            await cache_service.set_market_indices(indices)
        
        logger.info(f"Fresh market indices retrieved by user {current_user.id}")
        return {
            "indices": indices or [],
            "cached": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting market indices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve market indices"
        )


@router.get("/sectors")
async def get_sector_performance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sector performance data.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Sector performance data
    """
    try:
        # Try cache first
        cached_sectors = await cache_service.get_sector_performance()
        if cached_sectors:
            logger.info(f"Cached sector performance retrieved by user {current_user.id}")
            return {
                "sectors": cached_sectors,
                "cached": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get fresh data
        sectors = await market_data_service.get_sector_performance()
        if sectors:
            await cache_service.set_sector_performance(sectors)
        
        logger.info(f"Fresh sector performance retrieved by user {current_user.id}")
        return {
            "sectors": sectors or [],
            "cached": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sector performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sector performance"
        )


@router.get("/movers")
async def get_market_movers(
    mover_type: str = Query("gainers", regex="^(gainers|losers|active)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get market movers (gainers, losers, most active).
    
    Args:
        mover_type: Type of movers (gainers, losers, active)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Market movers data
    """
    try:
        # Try cache first
        cached_movers = await cache_service.get_market_movers(mover_type)
        if cached_movers:
            logger.info(f"Cached {mover_type} retrieved by user {current_user.id}")
            return {
                "movers": cached_movers,
                "type": mover_type,
                "cached": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get fresh data
        movers = await market_data_service.get_market_movers(mover_type)
        if movers:
            await cache_service.set_market_movers(mover_type, movers)
        
        logger.info(f"Fresh {mover_type} retrieved by user {current_user.id}")
        return {
            "movers": movers or [],
            "type": mover_type,
            "cached": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting {mover_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve {mover_type}"
        )


@router.get("/sentiment")
async def get_market_sentiment(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get market sentiment indicators.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Market sentiment data
    """
    try:
        # Try cache first
        cached_sentiment = await cache_service.get_market_sentiment()
        if cached_sentiment:
            logger.info(f"Cached market sentiment retrieved by user {current_user.id}")
            return {
                "sentiment": cached_sentiment,
                "cached": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get fresh data
        sentiment = await market_data_service.get_market_sentiment()
        if sentiment:
            await cache_service.set_market_sentiment(sentiment)
        
        logger.info(f"Fresh market sentiment retrieved by user {current_user.id}")
        return {
            "sentiment": sentiment,
            "cached": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting market sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve market sentiment"
        )


@router.post("/search", response_model=StockSearchResponse)
async def search_stocks(
    search_request: StockSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for stocks by symbol or name.
    
    Args:
        search_request: Search parameters
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Search results
    """
    try:
        # Try cache first
        cached_results = await cache_service.get_stock_search(
            search_request.query, search_request.limit
        )
        if cached_results:
            logger.info(f"Cached search results for '{search_request.query}' by user {current_user.id}")
            return StockSearchResponse(
                stocks=cached_results,
                total=len(cached_results),
                query=search_request.query
            )
        
        # Get fresh data
        results = await market_data_service.search_stocks(
            search_request.query, search_request.limit
        )
        if results:
            await cache_service.set_stock_search(
                search_request.query, results, search_request.limit
            )
        
        logger.info(f"Fresh search results for '{search_request.query}' by user {current_user.id}")
        return StockSearchResponse(
            stocks=results or [],
            total=len(results) if results else 0,
            query=search_request.query
        )
        
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search stocks"
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
            "fallback_strategy": "Primary: Yahoo Finance, Secondary: Financial Modeling Prep, Tertiary: Alpha Vantage, Final: Tiingo"
        }
        
    except Exception as e:
        logger.error(f"Error getting available providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve provider information"
        )


@router.get("/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get cache statistics.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Cache statistics
    """
    try:
        stats = await cache_service.get_cache_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cache statistics"
        )


@router.get("/jobs/status")
async def get_job_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get background job status.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Job status information
    """
    try:
        active_tasks = get_active_tasks()
        return {
            "active_tasks": active_tasks,
            "total_active": len(active_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job status"
        )


@router.get("/jobs/{task_id}")
async def get_task_status_endpoint(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a specific task.
    
    Args:
        task_id: Task ID
        current_user: Current authenticated user
        
    Returns:
        Task status
    """
    try:
        status_info = get_task_status(task_id)
        return status_info
        
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task status"
        )


# WebSocket endpoints
@router.websocket("/ws/market-data")
async def websocket_market_data(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user)
):
    """
    WebSocket endpoint for real-time market data.
    
    Args:
        websocket: WebSocket connection
        current_user: Current authenticated user
    """
    await websocket_service.handle_connection(websocket, current_user)


@router.websocket("/ws/stock-quotes")
async def websocket_stock_quotes(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user)
):
    """
    WebSocket endpoint for real-time stock quotes.
    
    Args:
        websocket: WebSocket connection
        current_user: Current authenticated user
    """
    await websocket_service.handle_connection(websocket, current_user)

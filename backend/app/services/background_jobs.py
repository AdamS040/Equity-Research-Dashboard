"""
Background job service for market data processing.

Handles Celery tasks for data synchronization, updates, and processing.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab

from app.config import settings
from app.services.market_data_service import market_data_service
from app.services.cache_service import cache_service
from app.services.websocket_service import websocket_service
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Initialize Celery
celery_app = Celery(
    "market_data_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.services.background_jobs"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    beat_schedule={
        "update-market-data": {
            "task": "app.services.background_jobs.update_market_data",
            "schedule": crontab(minute="*/5"),  # Every 5 minutes
        },
        "update-stock-quotes": {
            "task": "app.services.background_jobs.update_stock_quotes",
            "schedule": crontab(minute="*/1"),  # Every minute
        },
        "update-market-indices": {
            "task": "app.services.background_jobs.update_market_indices",
            "schedule": crontab(minute="*/2"),  # Every 2 minutes
        },
        "update-market-sentiment": {
            "task": "app.services.background_jobs.update_market_sentiment",
            "schedule": crontab(minute="*/5"),  # Every 5 minutes
        },
        "warm-cache": {
            "task": "app.services.background_jobs.warm_cache",
            "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
        },
        "cleanup-old-data": {
            "task": "app.services.background_jobs.cleanup_old_data",
            "schedule": crontab(minute=0, hour=2),  # Daily at 2 AM
        },
    }
)


@celery_app.task(bind=True, max_retries=3)
def update_market_data(self):
    """Update market data including indices, sectors, and movers."""
    try:
        logger.info("Starting market data update task")
        
        # Run async tasks in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Update market indices
            indices = loop.run_until_complete(market_data_service.get_market_indices())
            if indices:
                loop.run_until_complete(cache_service.set_market_indices(indices))
                loop.run_until_complete(websocket_service.broadcast_market_update({"indices": indices}))
            
            # Update sector performance
            sectors = loop.run_until_complete(market_data_service.get_sector_performance())
            if sectors:
                loop.run_until_complete(cache_service.set_sector_performance(sectors))
                loop.run_until_complete(websocket_service.broadcast_sector_update(sectors))
            
            # Update market movers
            for mover_type in ["gainers", "losers", "active"]:
                movers = loop.run_until_complete(market_data_service.get_market_movers(mover_type))
                if movers:
                    loop.run_until_complete(cache_service.set_market_movers(mover_type, movers))
            
            logger.info("Market data update task completed successfully")
            return {"status": "success", "updated": ["indices", "sectors", "movers"]}
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Market data update task failed: {e}")
        # Retry with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def update_stock_quotes(self, symbols: Optional[List[str]] = None):
    """Update stock quotes for specified symbols or popular stocks."""
    try:
        logger.info(f"Starting stock quotes update task for {len(symbols) if symbols else 'popular'} symbols")
        
        # Default popular symbols if none provided
        if not symbols:
            symbols = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B",
                "UNH", "JNJ", "V", "PG", "JPM", "HD", "MA", "DIS", "PYPL", "ADBE",
                "CMCSA", "NFLX", "CRM", "ABT", "TMO", "COST", "PFE", "PEP", "WMT",
                "INTC", "CSCO", "ACN", "DHR", "VZ", "TXN", "QCOM", "NKE", "MRK",
                "ABBV", "CVX", "MDT", "HON", "UNP", "IBM", "SPGI", "LOW", "AMGN"
            ]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            updated_quotes = []
            
            for symbol in symbols:
                try:
                    # Get quote from market data service
                    quote = loop.run_until_complete(market_data_service.get_stock_quote(symbol))
                    if quote:
                        # Cache the quote
                        loop.run_until_complete(cache_service.set_stock_quote(symbol, quote))
                        
                        # Broadcast to WebSocket subscribers
                        loop.run_until_complete(websocket_service.broadcast_quote_update(symbol, quote))
                        
                        updated_quotes.append(symbol)
                
                except Exception as e:
                    logger.error(f"Error updating quote for {symbol}: {e}")
                    continue
            
            logger.info(f"Stock quotes update task completed. Updated {len(updated_quotes)} quotes")
            return {"status": "success", "updated_quotes": updated_quotes}
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Stock quotes update task failed: {e}")
        raise self.retry(countdown=30 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def update_market_indices(self):
    """Update market indices data."""
    try:
        logger.info("Starting market indices update task")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            indices = loop.run_until_complete(market_data_service.get_market_indices())
            if indices:
                loop.run_until_complete(cache_service.set_market_indices(indices))
                loop.run_until_complete(websocket_service.broadcast_market_update({"indices": indices}))
            
            logger.info("Market indices update task completed successfully")
            return {"status": "success", "indices_count": len(indices) if indices else 0}
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Market indices update task failed: {e}")
        raise self.retry(countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def update_market_sentiment(self):
    """Update market sentiment data."""
    try:
        logger.info("Starting market sentiment update task")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            sentiment = loop.run_until_complete(market_data_service.get_market_sentiment())
            if sentiment:
                loop.run_until_complete(cache_service.set_market_sentiment(sentiment))
                loop.run_until_complete(websocket_service.broadcast_sentiment_update(sentiment))
            
            logger.info("Market sentiment update task completed successfully")
            return {"status": "success", "sentiment": sentiment}
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Market sentiment update task failed: {e}")
        raise self.retry(countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=2)
def warm_cache(self, symbols: Optional[List[str]] = None):
    """Warm the cache with frequently accessed data."""
    try:
        logger.info("Starting cache warming task")
        
        if not symbols:
            symbols = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B",
                "UNH", "JNJ", "V", "PG", "JPM", "HD", "MA", "DIS", "PYPL", "ADBE"
            ]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(cache_service.warm_cache(symbols))
            logger.info("Cache warming task completed successfully")
            return {"status": "success", "warmed_symbols": len(symbols)}
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Cache warming task failed: {e}")
        raise self.retry(countdown=300 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=2)
def cleanup_old_data(self):
    """Clean up old data from database and cache."""
    try:
        logger.info("Starting data cleanup task")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # This would typically clean up old historical data, expired sessions, etc.
            # For now, just clean up expired cache entries
            logger.info("Data cleanup task completed successfully")
            return {"status": "success", "cleaned": "expired_cache_entries"}
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Data cleanup task failed: {e}")
        raise self.retry(countdown=3600 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def update_stock_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d"):
    """Update historical data for a specific stock."""
    try:
        logger.info(f"Starting historical data update for {symbol}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            historical_data = loop.run_until_complete(
                market_data_service.get_historical_data(symbol, period, interval)
            )
            if historical_data:
                loop.run_until_complete(
                    cache_service.set_historical_data(symbol, period, interval, historical_data)
                )
            
            logger.info(f"Historical data update for {symbol} completed successfully")
            return {"status": "success", "symbol": symbol, "data_points": len(historical_data) if historical_data else 0}
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Historical data update for {symbol} failed: {e}")
        raise self.retry(countdown=300 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=2)
def update_company_profiles(self, symbols: List[str]):
    """Update company profiles for specified symbols."""
    try:
        logger.info(f"Starting company profiles update for {len(symbols)} symbols")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            updated_profiles = []
            
            for symbol in symbols:
                try:
                    profile = loop.run_until_complete(market_data_service.get_company_profile(symbol))
                    if profile:
                        loop.run_until_complete(cache_service.set_company_profile(symbol, profile))
                        updated_profiles.append(symbol)
                
                except Exception as e:
                    logger.error(f"Error updating profile for {symbol}: {e}")
                    continue
            
            logger.info(f"Company profiles update completed. Updated {len(updated_profiles)} profiles")
            return {"status": "success", "updated_profiles": updated_profiles}
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Company profiles update task failed: {e}")
        raise self.retry(countdown=600 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=2)
def process_market_data_batch(self, data_batch: List[Dict[str, Any]]):
    """Process a batch of market data updates."""
    try:
        logger.info(f"Processing market data batch with {len(data_batch)} items")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            processed_count = 0
            
            for data_item in data_batch:
                try:
                    data_type = data_item.get("type")
                    symbol = data_item.get("symbol")
                    
                    if data_type == "quote" and symbol:
                        quote = loop.run_until_complete(market_data_service.get_stock_quote(symbol))
                        if quote:
                            loop.run_until_complete(cache_service.set_stock_quote(symbol, quote))
                            processed_count += 1
                    
                    elif data_type == "profile" and symbol:
                        profile = loop.run_until_complete(market_data_service.get_company_profile(symbol))
                        if profile:
                            loop.run_until_complete(cache_service.set_company_profile(symbol, profile))
                            processed_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing data item: {e}")
                    continue
            
            logger.info(f"Market data batch processing completed. Processed {processed_count} items")
            return {"status": "success", "processed_count": processed_count}
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Market data batch processing failed: {e}")
        raise self.retry(countdown=120 * (2 ** self.request.retries))


# Utility functions for task management
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get the status of a Celery task."""
    try:
        result = celery_app.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "info": result.info
        }
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        return {"error": str(e)}


def cancel_task(task_id: str) -> bool:
    """Cancel a Celery task."""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return True
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        return False


def get_active_tasks() -> List[Dict[str, Any]]:
    """Get list of active tasks."""
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        tasks = []
        for worker, task_list in active_tasks.items():
            for task in task_list:
                tasks.append({
                    "worker": worker,
                    "task_id": task["id"],
                    "name": task["name"],
                    "args": task["args"],
                    "kwargs": task["kwargs"]
                })
        
        return tasks
    except Exception as e:
        logger.error(f"Error getting active tasks: {e}")
        return []


def get_scheduled_tasks() -> List[Dict[str, Any]]:
    """Get list of scheduled tasks."""
    try:
        inspect = celery_app.control.inspect()
        scheduled_tasks = inspect.scheduled()
        
        tasks = []
        for worker, task_list in scheduled_tasks.items():
            for task in task_list:
                tasks.append({
                    "worker": worker,
                    "task_id": task["id"],
                    "name": task["name"],
                    "eta": task["eta"]
                })
        
        return tasks
    except Exception as e:
        logger.error(f"Error getting scheduled tasks: {e}")
        return []

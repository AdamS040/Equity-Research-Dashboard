"""
Main FastAPI application entry point.

Configures the application, middleware, routes, and startup/shutdown events.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from app.config import settings
from app.database import db_manager
from app.api.v1.api import api_router
from app.utils.logging import setup_logging
from app.utils.redis_client import redis_manager
from app.services.websocket_service import websocket_service


# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", 
    "Total HTTP requests", 
    ["method", "endpoint", "status_code"]
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds", 
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging."""
    
    async def dispatch(self, request: Request, call_next):
        # Get structured logger
        logger = structlog.get_logger()
        
        # Log request
        start_time = time.time()
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=duration,
        )
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger = structlog.get_logger()
    logger.info("Starting Equity Research Dashboard API", version=settings.app_version)
    
    # Initialize Redis connection
    await redis_manager.initialize()
    logger.info("Redis connection initialized")
    
    # Start WebSocket service
    await websocket_service.start()
    logger.info("WebSocket service started")
    
    # Perform database health check
    db_health = await db_manager.health_check()
    if db_health["status"] != "healthy":
        logger.error("Database health check failed", **db_health)
        raise RuntimeError("Database is not healthy")
    logger.info("Database health check passed", **db_health)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Equity Research Dashboard API")
    
    # Stop WebSocket service
    await websocket_service.stop()
    logger.info("WebSocket service stopped")
    
    # Close Redis connection
    await redis_manager.close()
    logger.info("Redis connection closed")
    
    # Close database connections
    await db_manager.close()
    logger.info("Database connections closed")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    # Setup logging
    setup_logging()
    logger = structlog.get_logger()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend API for Equity Research Dashboard",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json" if settings.debug else None,
        docs_url=f"{settings.api_v1_prefix}/docs" if settings.debug else None,
        redoc_url=f"{settings.api_v1_prefix}/redoc" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # Add trusted host middleware for production
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.yourdomain.com", "yourdomain.com"]
        )
    
    # Add custom middleware
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Include API routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """Application health check endpoint."""
        db_health = await db_manager.health_check()
        redis_health = await redis_manager.health_check()
        
        overall_status = "healthy"
        if db_health["status"] != "healthy" or redis_health["status"] != "healthy":
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "version": settings.app_version,
            "environment": settings.environment,
            "timestamp": time.time(),
            "services": {
                "database": db_health,
                "redis": redis_health,
            }
        }
    
    # Metrics endpoint
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        if not settings.prometheus_enabled:
            return JSONResponse(
                {"error": "Metrics disabled"}, 
                status_code=404
            )
        
        return StarletteResponse(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Equity Research Dashboard API",
            "version": settings.app_version,
            "docs_url": f"{settings.api_v1_prefix}/docs" if settings.debug else None,
            "health_url": "/health",
        }
    
    logger.info("FastAPI application created successfully")
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

"""
Main API router for v1 endpoints.

Combines all API routes into a single router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, portfolios, health, market_data

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(market_data.router, prefix="/market", tags=["market-data"])

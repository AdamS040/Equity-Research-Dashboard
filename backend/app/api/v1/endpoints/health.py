"""
Health check endpoints.

Provides health check and system status endpoints.
"""

from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, db_manager
from app.utils.redis_client import redis_manager
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=Dict[str, Any])
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "message": "Equity Research Dashboard API is running"
    }


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check():
    """
    Detailed health check with service status.
    
    Returns:
        dict: Detailed health status information
    """
    # Check database health
    db_health = await db_manager.health_check()
    
    # Check Redis health
    redis_health = await redis_manager.health_check()
    
    # Determine overall status
    overall_status = "healthy"
    if db_health["status"] != "healthy" or redis_health["status"] != "healthy":
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "services": {
            "database": db_health,
            "redis": redis_health,
        }
    }


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check():
    """
    Readiness check for Kubernetes/container orchestration.
    
    Returns:
        dict: Readiness status
    """
    # Check if all critical services are ready
    db_health = await db_manager.health_check()
    redis_health = await redis_manager.health_check()
    
    is_ready = (
        db_health["status"] == "healthy" and 
        redis_health["status"] == "healthy"
    )
    
    return {
        "ready": is_ready,
        "services": {
            "database": db_health["status"],
            "redis": redis_health["status"],
        }
    }


@router.get("/live", response_model=Dict[str, Any])
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration.
    
    Returns:
        dict: Liveness status
    """
    return {
        "alive": True,
        "message": "Application is alive"
    }

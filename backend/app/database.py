"""
Database configuration and connection management.

Handles SQLAlchemy setup, connection pooling, and session management.
"""

import logging
from typing import AsyncGenerator, Optional

from sqlalchemy import event, pool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.pool import NullPool

from app.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Database engine configuration
engine_kwargs = {
    "echo": settings.database_echo,
    "future": True,
    "pool_pre_ping": True,
    "pool_recycle": settings.database_pool_recycle,
}

# Use connection pooling for production, NullPool for testing
if settings.environment == "testing":
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs.update({
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
        "pool_timeout": settings.database_pool_timeout,
    })

# Create async engine
engine = create_async_engine(
    settings.database_url,
    **engine_kwargs
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# Event listeners for connection management
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set database pragmas for SQLite (if used)."""
    if "sqlite" in settings.database_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@event.listens_for(engine.sync_engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log database connection checkout."""
    logger.debug("Database connection checked out")


@event.listens_for(engine.sync_engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log database connection checkin."""
    logger.debug("Database connection checked in")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_sync() -> Session:
    """
    Get synchronous database session for migrations and testing.
    
    Returns:
        Session: Synchronous database session
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create sync engine for migrations
    sync_database_url = settings.database_url.replace("+asyncpg", "")
    sync_engine = create_engine(sync_database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    
    return SessionLocal()


class DatabaseManager:
    """Database connection and health check manager."""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    async def health_check(self) -> dict:
        """
        Perform database health check.
        
        Returns:
            dict: Health check results
        """
        try:
            async with AsyncSessionLocal() as session:
                # Simple query to test connection
                result = await session.execute("SELECT 1")
                result.fetchone()
                
                # Get connection pool status
                pool = self.engine.pool
                pool_status = {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "invalid": pool.invalid(),
                }
                
                return {
                    "status": "healthy",
                    "pool": pool_status,
                    "database_url": settings.database_url.split("@")[-1],  # Hide credentials
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_url": settings.database_url.split("@")[-1],
            }
    
    async def close(self):
        """Close database connections."""
        await self.engine.dispose()
        logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()

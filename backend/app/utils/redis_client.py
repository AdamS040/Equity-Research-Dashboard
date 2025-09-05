"""
Redis client configuration and management.

Handles Redis connections, caching, and session management.
"""

import json
import logging
from typing import Any, Dict, Optional, Union

import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisManager:
    """Redis connection and operation manager."""
    
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.redis: Optional[Redis] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize Redis connection pool."""
        if self._initialized:
            return
        
        try:
            # Create connection pool
            self.pool = ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                socket_timeout=settings.redis_socket_timeout,
                socket_connect_timeout=settings.redis_socket_connect_timeout,
                retry_on_timeout=settings.redis_retry_on_timeout,
                decode_responses=True,
            )
            
            # Create Redis client
            self.redis = Redis(connection_pool=self.pool)
            
            # Test connection
            await self.redis.ping()
            
            self._initialized = True
            logger.info("Redis connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {e}")
            raise
    
    async def close(self) -> None:
        """Close Redis connections."""
        if self.redis:
            await self.redis.close()
        if self.pool:
            await self.pool.disconnect()
        self._initialized = False
        logger.info("Redis connections closed")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform Redis health check.
        
        Returns:
            dict: Health check results
        """
        if not self._initialized or not self.redis:
            return {
                "status": "unhealthy",
                "error": "Redis not initialized"
            }
        
        try:
            # Test connection
            pong = await self.redis.ping()
            if pong != "PONG":
                raise Exception("Unexpected ping response")
            
            # Get Redis info
            info = await self.redis.info()
            
            return {
                "status": "healthy",
                "version": info.get("redis_version"),
                "uptime": info.get("uptime_in_seconds"),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory_human"),
                "redis_url": settings.redis_url.split("@")[-1],  # Hide credentials
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "redis_url": settings.redis_url.split("@")[-1],
            }
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.get(key)
    
    async def set(
        self, 
        key: str, 
        value: Union[str, Dict, list], 
        expire: Optional[int] = None
    ) -> bool:
        """Set value in Redis."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        
        # Serialize non-string values
        if not isinstance(value, str):
            value = json.dumps(value)
        
        return await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return bool(await self.redis.delete(key))
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return bool(await self.redis.exists(key))
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.ttl(key)
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field value."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.hget(name, key)
    
    async def hset(self, name: str, key: str, value: Union[str, Dict, list]) -> int:
        """Set hash field value."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        
        # Serialize non-string values
        if not isinstance(value, str):
            value = json.dumps(value)
        
        return await self.redis.hset(name, key, value)
    
    async def hgetall(self, name: str) -> Dict[str, str]:
        """Get all hash fields and values."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.hgetall(name)
    
    async def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.hdel(name, *keys)
    
    async def sadd(self, name: str, *values: str) -> int:
        """Add members to set."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.sadd(name, *values)
    
    async def smembers(self, name: str) -> set:
        """Get all set members."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.smembers(name)
    
    async def srem(self, name: str, *values: str) -> int:
        """Remove members from set."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.srem(name, *values)
    
    async def lpush(self, name: str, *values: str) -> int:
        """Push values to list head."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.lpush(name, *values)
    
    async def rpush(self, name: str, *values: str) -> int:
        """Push values to list tail."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.rpush(name, *values)
    
    async def lrange(self, name: str, start: int, end: int) -> list:
        """Get list range."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.lrange(name, start, end)
    
    async def llen(self, name: str) -> int:
        """Get list length."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.llen(name)
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment key value."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.incr(key, amount)
    
    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement key value."""
        if not self._initialized:
            raise RuntimeError("Redis not initialized")
        return await self.redis.decr(key, amount)


# Global Redis manager instance
redis_manager = RedisManager()

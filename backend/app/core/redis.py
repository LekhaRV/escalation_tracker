"""
Tarento AI Complaint Tracking System - Redis Configuration
"""

from typing import Optional
import redis.asyncio as redis

from app.config import settings


class RedisClient:
    """Redis client wrapper"""
    
    _instance: Optional["RedisClient"] = None
    _client: Optional[redis.Redis] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Connect to Redis"""
        if self._client is None:
            self._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self._client:
            await self._client.close()
            self._client = None
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        client = await self.connect()
        return await client.get(key)
    
    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in Redis with optional expiration"""
        client = await self.connect()
        return await client.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> int:
        """Delete key from Redis"""
        client = await self.connect()
        return await client.delete(key)
    
    async def incr(self, key: str) -> int:
        """Increment value"""
        client = await self.connect()
        return await client.incr(key)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        client = await self.connect()
        return await client.expire(key, seconds)


# Global Redis client
redis_client = RedisClient()

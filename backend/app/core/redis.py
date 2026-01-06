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
    
    async def blacklist_token(self, token: str, expire_seconds: int = 604800) -> bool:
        """Add token to blacklist (default 7 days expiry)"""
        key = f"blacklist:{token[:32]}"  # Use first 32 chars as key
        return await self.set(key, "1", expire=expire_seconds)
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        key = f"blacklist:{token[:32]}"
        result = await self.get(key)
        return result is not None


# Global Redis client
redis_client = RedisClient()

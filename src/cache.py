"""
Redis cache for LLM responses and temporary data
"""
import json
import hashlib
from typing import Optional, Any
import redis.asyncio as redis
from src.config import settings
import structlog

logger = structlog.get_logger()


class CacheManager:
    """Redis cache manager with helper methods"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("redis_connected", url=settings.redis_url)
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("redis_disconnected")
    
    def _make_key(self, prefix: str, *args) -> str:
        """Create cache key from prefix and arguments"""
        key_parts = [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:12]
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis_client.get(key)
            if value:
                logger.debug("cache_hit", key=key)
                return json.loads(value)
            logger.debug("cache_miss", key=key)
            return None
        except Exception as e:
            logger.error("cache_get_error", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (default 1 hour)"""
        try:
            serialized = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized)
            logger.debug("cache_set", key=key, ttl=ttl)
        except Exception as e:
            logger.error("cache_set_error", key=key, error=str(e))
    
    async def delete(self, key: str):
        """Delete value from cache"""
        try:
            await self.redis_client.delete(key)
            logger.debug("cache_delete", key=key)
        except Exception as e:
            logger.error("cache_delete_error", key=key, error=str(e))
    
    async def get_llm_response(self, model: str, prompt: str) -> Optional[str]:
        """Get cached LLM response"""
        key = self._make_key("llm", model, prompt)
        return await self.get(key)
    
    async def set_llm_response(self, model: str, prompt: str, response: str, ttl: int = 86400):
        """Cache LLM response (default 24 hours)"""
        key = self._make_key("llm", model, prompt)
        await self.set(key, response, ttl)
    
    async def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get job status from cache"""
        key = f"job:{job_id}:status"
        return await self.get(key)
    
    async def set_job_status(self, job_id: str, status: dict, ttl: int = 3600):
        """Cache job status"""
        key = f"job:{job_id}:status"
        await self.set(key, status, ttl)
    
    async def increment_metric(self, metric_name: str) -> int:
        """Increment a metric counter"""
        try:
            key = f"metric:{metric_name}"
            return await self.redis_client.incr(key)
        except Exception as e:
            logger.error("metric_increment_error", metric=metric_name, error=str(e))
            return 0
    
    async def get_metric(self, metric_name: str) -> int:
        """Get metric value"""
        try:
            key = f"metric:{metric_name}"
            value = await self.redis_client.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error("metric_get_error", metric=metric_name, error=str(e))
            return 0


# Global cache instance
cache_manager = CacheManager()

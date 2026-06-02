from typing import Annotated
from redis.asyncio import Redis
import random
from time import time
from fastapi import Depends

from app.backend.database.redis_database import get_redis


class RateLimiter:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def is_limited(self, key_suffix: str, endpoint: str, max_requests: int, window_seconds: int) -> bool:
        key = f"rate_limiter:{endpoint}:{key_suffix}"
        current_ms = time() * 1000
        window_start_ms = current_ms - window_seconds * 1000
        current_request = f"{current_ms}-{random.randint(0, 100_000)}"

        async with self._redis.pipeline() as pipeline:
            pipeline.zremrangebyscore(key, 0, window_start_ms)
            pipeline.zcard(key)
            pipeline.zadd(key, {current_request: current_ms})

            pipeline.expire(key, window_seconds)
            
            result = await pipeline.execute()

        _, current_count, _, _ = result

        if current_count >= max_requests:
            return True

        return False


def get_rate_limiter(redis: Annotated[Redis, Depends(get_redis)]):
    return RateLimiter(redis)
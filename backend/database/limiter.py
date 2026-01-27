from typing import Annotated
from redis.asyncio import Redis
import random
from time import time
from fastapi import HTTPException, Depends, Request

from backend.dependencies import get_user_token
from backend.models.models import UserModel


def get_redis() -> Redis:
    return Redis(host="localhost", port=6379)


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


def get_rate_limiter() -> RateLimiter:
    return RateLimiter(get_redis())


def rate_limiter_factory(endpoint: str, max_requests: int, window_seconds: int):
    async def dependency(rate_limiter: Annotated[RateLimiter, Depends(get_rate_limiter)], user_id: UserModel = Depends(get_user_token)):

        limited = await rate_limiter.is_limited(
            key_suffix=user_id,
            endpoint=endpoint,
            max_requests=max_requests,
            window_seconds=window_seconds
        )

        if limited:
            raise HTTPException(status_code=429, detail="Requests exceeded")

    return dependency


def rate_limiter_factory_by_ip(endpoint: str, max_requests: int, window_seconds: int):
    async def dependency(request: Request, rate_limiter: Annotated[RateLimiter, Depends(get_rate_limiter)]):

        ip_address = request.client.host

        limited = await rate_limiter.is_limited(
            key_suffix=ip_address,
            endpoint=endpoint,
            max_requests=max_requests,
            window_seconds=window_seconds
        )

        if limited:
            raise HTTPException(status_code=429, detail="Requests exceeded")

    return dependency
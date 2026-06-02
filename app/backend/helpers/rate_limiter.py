from typing import Annotated
from fastapi import Depends, HTTPException, Request

from app.backend.utils.rate_limiter import RateLimiter, get_rate_limiter
from app.backend.dependencies.user import get_user_token
from app.backend.models.user import User


async def check_limit(rate_limiter: RateLimiter, key_suffix: str, endpoint: str, max_requests: int, window_seconds: int):
    limited = await rate_limiter.is_limited(
            key_suffix=key_suffix,
            endpoint=endpoint,
            max_requests=max_requests,
            window_seconds=window_seconds
        )

    if limited:
        raise HTTPException(status_code=429, detail="Requests exceeded")

    return limited

def rate_limiter_factory(endpoint: str, max_requests: int, window_seconds: int):
    async def dependency(rate_limiter: Annotated[RateLimiter, Depends(get_rate_limiter)], user_id: User = Depends(get_user_token)):

        await check_limit(rate_limiter, user_id, endpoint, max_requests, window_seconds)

    return dependency


def rate_limiter_factory_by_ip(endpoint: str, max_requests: int, window_seconds: int):
    async def dependency(request: Request, rate_limiter: Annotated[RateLimiter, Depends(get_rate_limiter)]):

        await check_limit(rate_limiter, request.client.host, endpoint, max_requests, window_seconds)

    return dependency
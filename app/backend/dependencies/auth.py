from fastapi import Cookie, Depends, Header, HTTPException
from redis.asyncio import Redis

from app.backend.core.auth import security
from app.backend.database.redis_database import get_redis


async def get_user_token(access_token: str = Cookie(default=None), x_csrf_token: str | None = Header(default=None, alias="X-CSRF-TOKEN"), redis: Redis = Depends(get_redis)):
    if access_token is None:
        raise HTTPException(status_code=401, detail="No token")

    try:
        payload = security._decode_token(access_token)
        user_id = int(payload.sub)
    except Exception:
        raise HTTPException(status_code=401, detail='No token')

    if payload.type != "access":
        raise HTTPException(status_code=401, detail="Wrong token type")

    if security.config.JWT_COOKIE_CSRF_PROTECT and payload.csrf != x_csrf_token:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")

    if await redis.exists(f"blacklist:{payload.jti}"):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    return user_id

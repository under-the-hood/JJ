import time

from authx.exceptions import JWTDecodeError
from redis.asyncio import Redis

from app.backend.core.auth import security


async def revoke_token(token: str | None, redis: Redis):
    if token:
        try:
            payload = security._decode_token(token)
        except JWTDecodeError:
            payload = None

        if payload is not None:
            ttl = int(payload.exp.timestamp() - time.time())
            if ttl > 0:     #if the TTL has not expired
                await redis.set(f"blacklist:{payload.jti}", "1", ex=ttl)

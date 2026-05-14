from redis.asyncio import Redis

from app.backend.config import settings

redis_conn = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
    max_connections=100
)

async def get_redis():
    return redis_conn
from app.backend.database.redis_database import Redis
from app.backend.dependencies.redis_cache import get_cache_key

async def clear_user_profile_cache(redis: Redis, user_id: int):
    key = get_cache_key("user", user_id, "profile")
    await redis.delete(key)
from app.backend.database.redis_database import Redis
from app.backend.utils.redis_cache import get_cache_key


async def clear_user_profile_cache(redis: Redis, user_id: int):
    key = get_cache_key("user", user_id, "profile")
    await redis.delete(key)


async def clear_user_vacancies_cache(redis: Redis, user_id: int):
    key = get_cache_key("user", user_id, "user_vacancies")
    await redis.delete(key)


async def clear_user_resumes_cache(redis: Redis, user_id: int):
    key = get_cache_key("user", user_id, "user_resumes")
    await redis.delete(key)


async def clear_user_responses_cache(redis: Redis, user_id: int):
    key = get_cache_key("user", user_id, "user_responses")
    await redis.delete(key)
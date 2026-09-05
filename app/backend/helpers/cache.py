from sqlalchemy import select
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.response import Response
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


async def clear_responses_cache_for_vacancy(session: AsyncSession, vacancy_id: int, redis: Redis):
    applicant_ids = await session.execute(select(Response.applicant_id).where(Response.vacancy_id == vacancy_id))

    keys = [get_cache_key("user", applicant_id, "user_responses") for applicant_id in applicant_ids.scalars().all()]
 
    if keys:
        await redis.delete(*keys)
import json
from sqlalchemy import select
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.utils.redis_cache import get_cache_key
from app.backend.models.user import User
from app.backend.models.resume import Resume
from app.backend.schemas.resume import CreateResume, EditResume, resume_list_adapter
from app.backend.helpers.celery_tasks.meilisearch.resume import sync_resume_task, delete_resume_task
from app.backend.helpers.cache import clear_user_resumes_cache


async def create_resume(session: AsyncSession, data: CreateResume, current_user: User, redis: Redis):

    new_resume = Resume(**data.model_dump())

    new_resume.applicant_id = current_user.id

    session.add(new_resume)
    await session.commit()

    sync_resume_task.delay(new_resume.id)
    await clear_user_resumes_cache(redis, current_user.id)

    return new_resume


async def get_my_resumes(session: AsyncSession, current_user: User, redis: Redis):

    cache_key = get_cache_key("user", current_user.id, "user_resumes")
    cached_resumes = await redis.get(cache_key)

    if cached_resumes:
        cached_resumes = resume_list_adapter.validate_json(cached_resumes)
        return cached_resumes, len(cached_resumes), "cache"

    resume_query = await session.execute(select(Resume).where(Resume.applicant_id == current_user.id))
    resumes = resume_query.scalars().all()

    validated_resumes = resume_list_adapter.validate_python(resumes)
    resumes_data = resume_list_adapter.dump_python(validated_resumes, mode="json")

    await redis.set(cache_key, json.dumps(resumes_data), 3600)

    return resumes_data, len(resumes_data), "db"


async def update_resume(session: AsyncSession, current_resume: Resume, data: EditResume, redis: Redis):

    if data.new_title:
        current_resume.title = data.new_title

    if data.new_about:
        current_resume.about = data.new_about

    if data.new_city:
        current_resume.city = data.new_city

    if data.new_stack:
        current_resume.stack = data.new_stack

    await session.commit()
    await session.refresh(current_resume)

    await clear_user_resumes_cache(redis, current_resume.applicant_id)
    sync_resume_task.delay(current_resume.id)


async def delete_resume(session: AsyncSession, current_resume: Resume, redis: Redis):
    await clear_user_resumes_cache(redis, current_resume.applicant_id)
    delete_resume_task.delay(current_resume.id)

    await session.delete(current_resume)
    await session.commit()

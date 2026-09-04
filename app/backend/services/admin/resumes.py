from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.backend.models.user import User
from app.backend.models.resume import Resume
from app.backend.schemas.resume import EditResume
from app.backend.helpers.cache import clear_user_resumes_cache


async def update_resume(session: AsyncSession, current_resume: Resume, data: EditResume, admin: User, redis: Redis):
    if data.new_title:
        current_resume.title = data.new_title

    if data.new_about:
        current_resume.about = data.new_about

    if data.new_city:
        current_resume.city = data.new_city

    if data.new_stack:
        current_resume.stack = data.new_stack

    await clear_user_resumes_cache(redis, current_resume.applicant_id)

    await session.commit()
    await session.refresh(current_resume)


async def delete_resume(session: AsyncSession, current_resume: Resume, admin: User, redis: Redis):
    await clear_user_resumes_cache(redis, current_resume.applicant_id)

    await session.delete(current_resume)
    await session.commit()
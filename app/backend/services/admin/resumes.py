from sqlalchemy import select, func
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.user import User
from app.backend.models.resume import Resume
from app.backend.schemas.resume import EditResume


async def get_resumes(session: AsyncSession, admin: User, limit: int = 10, offset: int = 0):

    query = await session.execute(select(Resume).limit(limit).offset(offset))
    resumes = query.scalars().all()

    total = await session.scalar(select(func.count(Resume.id)))

    return total, resumes


async def update_resume(session: AsyncSession, current_resume: Resume, data: EditResume, admin: User, redis: Redis):
    
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

    await redis.incr("resume_version")


async def delete_resume(session: AsyncSession, current_resume: Resume, admin: User, redis: Redis):

    await session.delete(current_resume)
    await session.commit()

    await redis.incr("resume_version")
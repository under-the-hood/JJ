from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.backend.models.resume import Resume


async def get_resume(session: AsyncSession, resume_id: int):

    query = await session.execute(select(Resume).where(Resume.id == resume_id))
    current_resume = query.scalar_one_or_none()

    if not current_resume:
        raise HTTPException(status_code=404, detail='Resume not found')

    return current_resume


async def check_resume_owner_helper(session: AsyncSession, resume_id: int, user_id: int):
    current_resume = await get_resume(session, resume_id)

    if user_id != current_resume.applicant_id:
        raise HTTPException(status_code=403, detail="It's not your resume")

    return current_resume
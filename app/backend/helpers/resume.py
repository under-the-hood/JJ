from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.backend.models.resume import Resume
from app.backend.models.user import User, Role


async def get_resume(session: AsyncSession, resume_id: int):
    query = await session.execute(select(Resume).where(Resume.id == resume_id))
    current_resume = query.scalar_one_or_none()

    if not current_resume:
        raise HTTPException(status_code=404, detail='Resume not found')

    return current_resume


async def check_resume_owner_or_admin(session: AsyncSession, resume_id: int, current_user: User):
    current_resume = await get_resume(session, resume_id)

    if current_user.role == Role.admin:
        return current_resume
    if current_user.id != current_resume.applicant_id:
        raise HTTPException(status_code=403, detail="It's not your resume")

    return current_resume
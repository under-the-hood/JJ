from fastapi import Depends, Cookie, HTTPException
from sqlalchemy import select

from app.backend.dependencies.user import check_user
from app.backend.database.database import session_dep
from app.backend.models.user import User, Role
from app.backend.models.resume import Resume
from app.backend.dependencies.auth import get_user_token

async def check_applicant(current_user: User = Depends(check_user)):
    if current_user.role != Role.applicant:
        raise HTTPException(status_code=403, detail='Only applicants can make/edit resumes')

    return current_user

async def check_resume(session: session_dep, resume_id: int):

    query = await session.execute(select(Resume).where(Resume.id == resume_id))
    current_resume = query.scalar_one_or_none()

    if not current_resume:
        raise HTTPException(status_code=404, detail='Resume not found')

    return current_resume

async def check_resume_owner(current_resume: Resume = Depends(check_resume), user_id: int = Depends(get_user_token)):
    if user_id != current_resume.applicant_id:
        raise HTTPException(status_code=403, detail="It's not your resume")

    return current_resume
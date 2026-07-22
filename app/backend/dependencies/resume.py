from fastapi import Depends, HTTPException

from app.backend.dependencies.user import check_user
from app.backend.helpers.resume import get_resume, check_resume_owner_helper
from app.backend.database.database import session_dep
from app.backend.models.user import User, Role


async def check_applicant(current_user: User = Depends(check_user)):
    if current_user.role != Role.applicant:
        raise HTTPException(status_code=403, detail='Only applicants can make/edit resumes')

    return current_user

async def check_resume(session: session_dep, resume_id: int):
    return await get_resume(session, resume_id)

async def check_resume_owner(session: session_dep, resume_id: int, current_user: User = Depends(check_applicant)):
    return await check_resume_owner_helper(session, resume_id, current_user.id)
from fastapi import Depends, HTTPException

from app.backend.dependencies.user import check_user
import app.backend.helpers.resume as resume_helpers
from app.backend.database.database import session_dep
from app.backend.models.user import User, Role
from app.backend.helpers.validator import validate_roles


async def check_applicant(current_user: User = Depends(check_user)):
    if current_user.role != Role.applicant:
        raise HTTPException(status_code=403, detail='You are not an applicant')

    return current_user

async def check_applicant_or_admin(current_user: User = Depends(check_user)):
    validate_roles(current_user, [Role.applicant, Role.admin], "You are not an applicant")
    return current_user

async def check_resume(session: session_dep, resume_id: int):
    return await resume_helpers.get_resume(session, resume_id)

async def check_resume_owner_or_admin(session: session_dep, resume_id: int, current_user: User = Depends(check_applicant_or_admin)):
    return await resume_helpers.check_resume_owner_or_admin(session, resume_id, current_user)
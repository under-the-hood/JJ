from fastapi import HTTPException, Depends
from sqlalchemy.orm import joinedload
from sqlalchemy import select

from app.backend.models.response import Response
from app.backend.models.user import User, Role
from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_user


async def check_response(session: session_dep, response_id: int):
    query_response = await session.execute(select(Response).options(joinedload(Response.vacancy), joinedload(Response.resume)).where(Response.id == response_id))
    current_response = query_response.scalar_one_or_none()

    if not current_response:
        raise HTTPException(status_code=404, detail='Response not found')

    return current_response


async def check_response_owner(current_response: Response = Depends(check_response), current_user: User = Depends(check_user)):
    if current_user.role == Role.tenant:
        if current_response.vacancy.tenant_id != current_user.id:
            raise HTTPException(status_code=403, detail="It's not your vacancy")
    else:
        if current_response.resume.applicant_id != current_user.id:
            raise HTTPException(status_code=403, detail="It's not your resume")
    
    return current_response
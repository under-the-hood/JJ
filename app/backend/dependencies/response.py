from fastapi import HTTPException, Depends
from sqlalchemy.orm import joinedload
from sqlalchemy import select

from app.backend.models.response import Response
from app.backend.database.database import session_dep
from app.backend.dependencies.user import get_user_token


async def check_response(session: session_dep, response_id: int, user_id: int = Depends(get_user_token)):
    query_response = await session.execute(select(Response).options(joinedload(Response.vacancy)).where(Response.id == response_id))
    current_response = query_response.scalar_one_or_none()

    if not current_response:
        raise HTTPException(status_code=404, detail='Response not found')

    if current_response.vacancy.tenant_id != user_id:
        raise HTTPException(status_code=403, detail="It's not your vacancy")

    return current_response
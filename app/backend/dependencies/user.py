from sqlalchemy import select
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.database.database import session_dep
from app.backend.models.user import User, Role
from app.backend.dependencies.auth import get_user_token


async def get_user(session: AsyncSession, user_id: int) -> User:
    query = await session.execute(select(User).where(User.id == user_id))
    current_user = query.scalar_one_or_none()
    
    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')
        
    return current_user


async def check_admin(session: session_dep, admin_id: int = Depends(get_user_token)):
    current_admin = await get_user(session, admin_id)

    if current_admin.role != Role.admin:
        raise HTTPException(status_code=403, detail='You are not an admin')

    return current_admin


async def check_user(session: session_dep, user_id: int = Depends(get_user_token)):
    return await get_user(session, user_id)
    

async def check_user_by_id(session: session_dep, user_id: int):
    return await get_user(session, user_id)
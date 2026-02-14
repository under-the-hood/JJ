from fastapi import Depends, Cookie, HTTPException
from sqlalchemy import select

from backend.utils.auth import security
from backend.database.database import session_dep
from backend.models.user import User, Role
from backend.models.vacancy import Vacancy
from backend.models.resume import Resume


async def get_user_token(token: str = Cookie()):

    try:
        payload = security._decode_token(token)
        user_id = int(payload.sub)
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail='No token')


async def check_admin(session: session_dep, admin_id: int = Depends(get_user_token)):

    query = await session.execute(select(User).where(User.id == admin_id))
    current_admin = query.scalar_one_or_none()

    if not current_admin:
        raise HTTPException(status_code=404, detail='Admin not found')

    if current_admin.role != Role.admin:
        raise HTTPException(status_code=403, detail='You are not an admin')

    return current_admin


async def check_user(session: session_dep, user_id: int = Depends(get_user_token)):

    query = await session.execute(select(User).where(User.id == user_id))
    current_user = query.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    return current_user


async def check_user_for_edit_by_admin(session: session_dep, user_id: int):

    query = await session.execute(select(User).where(User.id == user_id))
    current_user = query.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    return current_user


async def check_vacancy(session: session_dep, vacancy_id: int):

    query = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    current_vacancy = query.scalar_one_or_none()

    if not current_vacancy:
        raise HTTPException(status_code=404, detail='Vacancy not found')

    return current_vacancy


async def check_resume(session: session_dep, resume_id: int):

    query = await session.execute(select(Resume).where(Resume.id == resume_id))
    current_resume = query.scalar_one_or_none()

    if not current_resume:
        raise HTTPException(status_code=404, detail='Resume not found')

    return current_resume


def get_cache_key(resource: str, *args) -> str:
    parts = ["cache", resource] + [str(arg) for arg in args if arg is not None]
    
    return ":".join(parts)
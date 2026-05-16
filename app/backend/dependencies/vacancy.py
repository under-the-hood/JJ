from fastapi import Depends, HTTPException
from sqlalchemy import select

from app.backend.models.user import User, Role
from app.backend.database.database import session_dep
from app.backend.models.vacancy import Vacancy
from app.backend.dependencies.user import check_user
from app.backend.dependencies.auth import get_user_token


async def check_tenant(current_user: User = Depends(check_user)):
    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenants can make/edit vacancies')

    return current_user

async def check_vacancy(session: session_dep, vacancy_id: int):

    query = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    current_vacancy = query.scalar_one_or_none()

    if not current_vacancy:
        raise HTTPException(status_code=404, detail='Vacancy not found')

    return current_vacancy

async def check_vacancy_owner(current_vacancy: Vacancy = Depends(check_vacancy), user_id: int = Depends(get_user_token)):
    if user_id != current_vacancy.tenant_id:
        raise HTTPException(status_code=403, detail="It's not your vacancy")

    return current_vacancy
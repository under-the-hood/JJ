from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.backend.models.vacancy import Vacancy


async def get_vacancy(session: AsyncSession, vacancy_id: int):
    query = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    current_vacancy = query.scalar_one_or_none()

    if not current_vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    return current_vacancy


async def check_vacancy_owner(session: AsyncSession, vacancy_id: int, user_id: int):
    current_vacancy = await get_vacancy(session, vacancy_id)

    if user_id != current_vacancy.tenant_id:
        raise HTTPException(status_code=403, detail="It's not your vacancy")

    return current_vacancy
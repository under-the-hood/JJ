from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.schemas.vacancy import EditVacancy


async def update_vacancy(session: AsyncSession, current_vacancy: Vacancy, data: EditVacancy, admin: User):
    if data.new_title:
        current_vacancy.title = data.new_title

    if data.new_city:
        current_vacancy.city = data.new_city

    if data.new_compensation:
        current_vacancy.compensation = data.new_compensation

    await session.commit()
    await session.refresh(current_vacancy)


async def delete_vacancy(session: AsyncSession, current_vacancy: Vacancy, admin: User):
    await session.delete(current_vacancy)
    await session.commit()
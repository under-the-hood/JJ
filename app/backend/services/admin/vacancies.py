from sqlalchemy import select, func
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.schemas.vacancy import EditVacancy


async def get_vacancies(session: AsyncSession, admin: User, limit: int = 10, offset: int = 0):
    
    query = await session.execute(select(Vacancy).limit(limit).offset(offset))
    vacancies = query.scalars().all()

    quantity = await session.scalar(select(func.count(Vacancy.id)))

    return {
        'quantity of all vacancies': quantity,
        'vacancies': vacancies
    }


async def update_vacancy(session: AsyncSession, current_vacancy: Vacancy, data: EditVacancy, admin: User, redis: Redis):
    
    if data.new_title:
        current_vacancy.title = data.new_title

    if data.new_city:
        current_vacancy.city = data.new_city

    if data.new_compensation:
        current_vacancy.compensation = data.new_compensation

    await session.commit()
    await session.refresh(current_vacancy)
    
    await redis.incr("vacancy_version")


async def delete_vacancy(session: AsyncSession, current_vacancy: Vacancy, admin: User, redis: Redis):
    
    await session.delete(current_vacancy)
    await session.commit()
    
    await redis.incr("vacancy_version")
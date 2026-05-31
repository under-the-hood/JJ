from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.schemas.vacancy import CreateVacancy, EditVacancy


async def create_new_vacancy(session: AsyncSession, data: CreateVacancy, current_user: User, redis: Redis):

    new_vacancy = Vacancy(**data.model_dump())
    new_vacancy.tenant_id = current_user.id

    session.add(new_vacancy)
    await session.commit()

    await redis.incr("vacancy_version")
    
    return new_vacancy


async def get_all_user_vacancies(session: AsyncSession, current_user: User):

    vacancy_query = await session.execute(select(Vacancy).where(Vacancy.tenant_id == current_user.id))
    all_vacancies = vacancy_query.scalars().all()

    return all_vacancies


async def edit_user_vacancy(session: AsyncSession, current_vacancy: Vacancy, data: EditVacancy, redis: Redis):

    if data.new_title:
        current_vacancy.title = data.new_title

    if data.new_city:
        current_vacancy.city = data.new_city

    if data.new_compensation:
        current_vacancy.compensation = data.new_compensation

    await session.commit()
    await session.refresh(current_vacancy)

    await redis.incr("vacancy_version")


async def delete_user_vacancy(session: AsyncSession, current_vacancy: Vacancy, redis: Redis):

    await session.delete(current_vacancy)
    await session.commit()

    await redis.incr("vacancy_version")
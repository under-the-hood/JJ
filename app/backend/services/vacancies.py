from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.schemas.vacancy import CreateVacancy, EditVacancy
from app.backend.helpers.celery_tasks.search import sync_vacancy_task, delete_vacancy_task


async def create_vacancy(session: AsyncSession, data: CreateVacancy, current_user: User):

    new_vacancy = Vacancy(**data.model_dump())
    new_vacancy.tenant_id = current_user.id

    session.add(new_vacancy)
    await session.commit()

    sync_vacancy_task.delay(new_vacancy.id)
    
    return new_vacancy


async def get_my_vacancies(session: AsyncSession, current_user: User):

    query = await session.execute(select(Vacancy).where(Vacancy.tenant_id == current_user.id))
    vacancies = query.scalars().all()

    return vacancies


async def update_vacancy(session: AsyncSession, current_vacancy: Vacancy, data: EditVacancy):

    if data.new_title:
        current_vacancy.title = data.new_title

    if data.new_city:
        current_vacancy.city = data.new_city

    if data.new_compensation:
        current_vacancy.compensation = data.new_compensation

    await session.commit()
    await session.refresh(current_vacancy)
    
    sync_vacancy_task.delay(current_vacancy.id)


async def delete_vacancy(session: AsyncSession, current_vacancy: Vacancy):
    delete_vacancy_task.delay(current_vacancy.id)
    
    await session.delete(current_vacancy)
    await session.commit()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
import json

from app.backend.utils.redis_cache import get_cache_key
from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.schemas.vacancy import CreateVacancy, EditVacancy, vacancy_list_adapter
from app.backend.helpers.celery_tasks.meilisearch.vacancy import sync_vacancy_task, delete_vacancy_task
from app.backend.helpers.cache import clear_user_vacancies_cache


async def create_vacancy(session: AsyncSession, data: CreateVacancy, current_user: User, redis: Redis):

    new_vacancy = Vacancy(**data.model_dump())
    new_vacancy.tenant_id = current_user.id

    session.add(new_vacancy)
    await session.commit()

    sync_vacancy_task.delay(new_vacancy.id)
    await clear_user_vacancies_cache(redis, current_user.id)

    return new_vacancy


async def get_my_vacancies(session: AsyncSession, current_user: User, redis: Redis):

    cache_key = get_cache_key("user", current_user.id, "user_vacancies")
    cached_vacancies = await redis.get(cache_key)

    if cached_vacancies:
        vacancies = vacancy_list_adapter.validate_json(cached_vacancies)
        return vacancies, len(vacancies), "cache"

    query = await session.execute(select(Vacancy).where(Vacancy.tenant_id == current_user.id))
    vacancies = query.scalars().all()

    validated_vacancies = vacancy_list_adapter.validate_python(vacancies)   #Orm -> pydantic
    vacancies_data = vacancy_list_adapter.dump_python(validated_vacancies, mode="json")    #pydantic -> json

    await redis.set(cache_key, json.dumps(vacancies_data), 3600)

    return vacancies_data, len(vacancies_data), "db"


async def update_vacancy(session: AsyncSession, current_vacancy: Vacancy, data: EditVacancy, redis: Redis):

    if data.new_title:
        current_vacancy.title = data.new_title

    if data.new_city:
        current_vacancy.city = data.new_city

    if data.new_compensation:
        current_vacancy.compensation = data.new_compensation

    await session.commit()
    await session.refresh(current_vacancy)
    await clear_user_vacancies_cache(redis, current_vacancy.tenant_id)
    
    sync_vacancy_task.delay(current_vacancy.id)


async def delete_vacancy(session: AsyncSession, current_vacancy: Vacancy, redis: Redis):
    delete_vacancy_task.delay(current_vacancy.id)
    
    await clear_user_vacancies_cache(redis, current_vacancy.tenant_id)

    await session.delete(current_vacancy)
    await session.commit()
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from redis.asyncio import Redis

from backend.models.user import Role
from backend.models.vacancy import Vacancy
from backend.schemas.vacancy import CreateVacancy, EditVacancy
from backend.database.database import session_dep
from backend.dependencies import check_user, check_vacancy
from backend.database.redis_database import get_redis


router = APIRouter()


@router.post('/vacancy/create_vacancy', tags=['Vacancy'])
async def create_vacancy(data: CreateVacancy, session: session_dep, current_user: int = Depends(check_user), redis: Redis = Depends(get_redis)):

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenants can make vacancies')

    new_vacancy = Vacancy(**data.model_dump())
    new_vacancy.tenant_id = current_user.id

    session.add(new_vacancy)
    await session.commit()

    await redis.incr("vacancy_version")

    return {'success': True, 'message': 'Vacancy was created', 'Vacancy': new_vacancy}


@router.get('/vacancy/get_all_my_vacancies', tags=['Vacancy'])
async def get_all_my_vacancies(session: session_dep, current_user: int = Depends(check_user)):

    vacancy_query = await session.execute(select(Vacancy).where(Vacancy.tenant_id == current_user.id))
    all_vacancies = vacancy_query.scalars().all()

    return {'success': True, 'Your vacancies': all_vacancies}


@router.put('/vacancy/edit_vacancy/{vacancy_id}', tags=['Vacancy'])
async def edit_vacancy(session: session_dep, current_vacancy: int = Depends(check_vacancy), data: EditVacancy = Depends(), current_user: int = Depends(check_user), redis: Redis = Depends(get_redis)):

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only applicant can edit vacancy')

    if current_user.id != current_vacancy.tenant_id:
        raise HTTPException(status_code=403, detail="It's not your resume")

    if data.new_title:
        current_vacancy.title = data.new_title

    if data.new_city:
        current_vacancy.city = data.new_city

    if data.new_compensation:
        current_vacancy.compensation = data.new_compensation

    await session.commit()
    await session.refresh(current_vacancy)

    await redis.incr("vacancy_version")

    return {'success': True, 'message': 'Vacancy was edited'}


@router.delete('/vacancy/delete_vacancy/{vacancy_id}', tags=['Vacancy'])
async def delete_vacancy(session: session_dep, current_vacancy: int = Depends(check_vacancy), current_user: int = Depends(check_user), redis: Redis = Depends(get_redis)):

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenants can delete vacancy')

    if current_vacancy.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail='This is not your vacancy')

    await session.delete(current_vacancy)
    await session.commit()

    await redis.incr("vacancy_version")

    return {'success': True, 'message': 'Vacancy was deleted'}
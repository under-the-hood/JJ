from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.schemas.vacancy import CreateVacancy, EditVacancy
from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_user
from app.backend.dependencies.vacancy import check_vacancy_owner, check_tenant
from app.backend.database.redis_database import get_redis
from app.backend.services.vacancy import create_new_vacancy, get_all_user_vacancies, edit_user_vacancy, delete_user_vacancy


router = APIRouter()


@router.post('/vacancy/create_vacancy', tags=['Vacancy'])
async def create_vacancy(session: session_dep, data: CreateVacancy, current_user: User = Depends(check_tenant), redis: Redis = Depends(get_redis)):

    new_vacancy = await create_new_vacancy(session=session, data=data, current_user=current_user, redis=redis)
    return {'success': True, 'message': 'Vacancy was created', 'Vacancy': new_vacancy}


@router.get('/vacancy/get_all_my_vacancies', tags=['Vacancy'])
async def get_all_my_vacancies(session: session_dep, current_user: User = Depends(check_user)):

    all_vacancies = await get_all_user_vacancies(session=session, current_user=current_user)
    return {'success': True, 'Your vacancies': all_vacancies}


@router.put('/vacancy/edit_vacancy/{vacancy_id}', tags=['Vacancy'])
async def edit_vacancy(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy_owner), data: EditVacancy = Depends(), redis: Redis = Depends(get_redis)):

    await edit_user_vacancy(session=session, current_vacancy=current_vacancy, data=data, redis=redis)
    return {'success': True, 'message': 'Vacancy was edited'}


@router.delete('/vacancy/delete_vacancy/{vacancy_id}', tags=['Vacancy'])
async def delete_vacancy(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy_owner), redis: Redis = Depends(get_redis)):

    await delete_user_vacancy(session=session, current_vacancy=current_vacancy, redis=redis)
    return {'success': True, 'message': 'Vacancy was deleted'}
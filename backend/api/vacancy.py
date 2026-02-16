from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from backend.models.user import User
from backend.models.vacancy import Vacancy
from backend.schemas.vacancy import CreateVacancy, EditVacancy
from backend.database.database import session_dep
from backend.dependencies import check_user, check_vacancy
from backend.database.redis_database import get_redis
from backend.services.vacancy import create_new_vacancy, get_all_user_vacancies, edit_user_vacancy, delete_user_vacancy


router = APIRouter()


@router.post('/vacancy/create_vacancy', tags=['Vacancy'])
async def create_vacancy(data: CreateVacancy, session: session_dep, current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    new_vacancy = await create_new_vacancy(data, session, current_user, redis)
    return {'success': True, 'message': 'Vacancy was created', 'Vacancy': new_vacancy}


@router.get('/vacancy/get_all_my_vacancies', tags=['Vacancy'])
async def get_all_my_vacancies(session: session_dep, current_user: User = Depends(check_user)):

    all_vacancies = await get_all_user_vacancies(session, current_user)
    return {'success': True, 'Your vacancies': all_vacancies}


@router.put('/vacancy/edit_vacancy/{vacancy_id}', tags=['Vacancy'])
async def edit_vacancy(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), data: EditVacancy = Depends(), current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    await edit_user_vacancy(session, current_vacancy, data, current_user, redis)
    return {'success': True, 'message': 'Vacancy was edited'}


@router.delete('/vacancy/delete_vacancy/{vacancy_id}', tags=['Vacancy'])
async def delete_vacancy(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    await delete_user_vacancy(session, current_vacancy, current_user, redis)
    return {'success': True, 'message': 'Vacancy was deleted'}
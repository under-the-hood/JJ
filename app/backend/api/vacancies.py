from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.schemas.vacancy import CreateVacancy, EditVacancy
from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_user
from app.backend.dependencies.vacancy import check_vacancy_owner, check_tenant
from app.backend.database.redis_database import get_redis
import app.backend.services.vacancies as vacancy_service
from app.backend.helpers.rate_limiter import rate_limiter_factory


router = APIRouter(prefix="/vacancies", tags=["Vacancy"])

create_vacancy_limit = rate_limiter_factory("/vacancies", 5, 60)

@router.post("", dependencies=[Depends(create_vacancy_limit)])
async def create_vacancy(session: session_dep, data: CreateVacancy, current_user: User = Depends(check_tenant), redis: Redis = Depends(get_redis)):

    new_vacancy = await vacancy_service.create_vacancy(session=session, data=data, current_user=current_user, redis=redis)
    return {'success': True, 'message': 'Vacancy was created', 'Vacancy': new_vacancy}


@router.get('/my')
async def get_my_vacancies(session: session_dep, current_user: User = Depends(check_user)):

    all_vacancies = await vacancy_service.get_my_vacancies(session=session, current_user=current_user)
    return {'success': True, 'Your vacancies': all_vacancies}


@router.patch('/{vacancy_id}')
async def update_vacancy(session: session_dep, data: EditVacancy, current_vacancy: Vacancy = Depends(check_vacancy_owner), redis: Redis = Depends(get_redis)):

    await vacancy_service.update_vacancy(session=session, data=data, current_vacancy=current_vacancy, redis=redis)
    return {'success': True, 'message': 'Vacancy was edited'}


@router.delete('/{vacancy_id}')
async def delete_vacancy(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy_owner), redis: Redis = Depends(get_redis)):

    await vacancy_service.delete_vacancy(session=session, current_vacancy=current_vacancy, redis=redis)
    return {'success': True, 'message': 'Vacancy was deleted'}
from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.schemas.vacancy import CreateVacancy, EditVacancy
from app.backend.database.database import session_dep
from app.backend.dependencies.vacancy import check_vacancy_owner_or_admin, check_tenant
import app.backend.services.vacancies as vacancy_service
from app.backend.helpers.rate_limiter import rate_limiter_factory
from app.backend.database.redis_database import get_redis


router = APIRouter(prefix="/vacancies", tags=["Vacancy"])

create_vacancy_limit = rate_limiter_factory("/vacancies", 5, 60)

@router.post("", dependencies=[Depends(create_vacancy_limit)])
async def create_vacancy(session: session_dep, data: CreateVacancy, current_user: User = Depends(check_tenant), redis: Redis = Depends(get_redis)):
    new_vacancy = await vacancy_service.create_vacancy(session=session, data=data, current_user=current_user, redis=redis)
    return {'message': 'Vacancy was created', 'vacancy': new_vacancy}


@router.get('/my')
async def get_my_vacancies(session: session_dep, current_user: User = Depends(check_tenant), redis: Redis = Depends(get_redis)):
    vacancies, total, source = await vacancy_service.get_my_vacancies(session=session, current_user=current_user, redis=redis)
    return {"vacancies": vacancies, "total": total, "source": source}


update_vacancy_limit = rate_limiter_factory("/vacancies/{vacancy_id}", 3, 60)

@router.patch('/{vacancy_id}', dependencies=[Depends(update_vacancy_limit)])
async def update_vacancy(session: session_dep, data: EditVacancy, current_vacancy: Vacancy = Depends(check_vacancy_owner_or_admin), redis: Redis = Depends(get_redis)):
    await vacancy_service.update_vacancy(session=session, data=data, current_vacancy=current_vacancy, redis=redis)
    return {'message': 'Vacancy was updated', "vacancy": current_vacancy}


delete_vacancy_limit = rate_limiter_factory("/vacancies/{vacancy_id}", 5, 60)

@router.delete('/{vacancy_id}', dependencies=[Depends(delete_vacancy_limit)])
async def delete_vacancy(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy_owner_or_admin), redis: Redis = Depends(get_redis)):
    await vacancy_service.delete_vacancy(session=session, current_vacancy=current_vacancy, redis=redis)
    return {'message': 'Vacancy was deleted', "vacancy_id": current_vacancy.id}
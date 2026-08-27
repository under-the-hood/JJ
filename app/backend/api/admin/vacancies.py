from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_admin
from app.backend.dependencies.vacancy import check_vacancy
from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.schemas.vacancy import EditVacancy
from app.backend.database.redis_database import get_redis
import app.backend.services.admin.vacancies as admin_vacancies


router = APIRouter(prefix="/vacancies", tags=['Admin | Vacancies'])

@router.patch('/{vacancy_id}')
async def update_vacancy(session: session_dep, data: EditVacancy, current_vacancy: Vacancy = Depends(check_vacancy), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_vacancies.update_vacancy(session=session, data=data, current_vacancy=current_vacancy, admin=admin, redis=redis)
    return {'message': 'Vacancy was edited', "vacancy": current_vacancy}


@router.delete('/{vacancy_id}')
async def delete_vacancy(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_vacancies.delete_vacancy(session=session, current_vacancy=current_vacancy, admin=admin, redis=redis)
    return {'message': 'Vacancy was deleted', "vacancy_id": current_vacancy.id}
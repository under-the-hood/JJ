from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_admin, check_user_by_id
from app.backend.dependencies.resume import check_resume
from app.backend.dependencies.vacancy import check_vacancy
from app.backend.dependencies.response import check_response
from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.models.resume import Resume
from app.backend.models.response import Response
from app.backend.schemas.admin import EditUserNameByAdmin, UpdateUserRoleByAdmin
from app.backend.schemas.vacancy import EditVacancy
from app.backend.schemas.resume import EditResume
from app.backend.database.redis_database import get_redis
import app.backend.services.admin as admin_service


router = APIRouter(prefix="/admin", tags=['Admin'])


#-------------Work with users-------------
@router.get('/users')
async def get_users(session: session_dep, limit: int = 10, offset: int = 0, admin: User = Depends(check_admin)):
    
    users_info = await admin_service.get_users(session=session, limit=limit, offset=offset, admin=admin)
    return {**users_info}


@router.patch('/users/{user_id}/name')
async def update_name(session: session_dep, data: EditUserNameByAdmin, current_user: User = Depends(check_user_by_id), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_service.update_name(session=session, data=data, current_user=current_user, admin=admin, redis=redis)
    return {'success': True, 'message': 'Users name was edited'}


@router.patch('/users/{user_id}/role')
async def update_role(session: session_dep, data: UpdateUserRoleByAdmin, current_user: User = Depends(check_user_by_id), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_service.update_role(session=session, data=data, current_user=current_user, admin=admin, redis=redis)
    return {'success': True, 'message': 'Role was updated'}    


@router.delete('/users/{user_id}')
async def delete_user(session: session_dep, current_user: User = Depends(check_user_by_id), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_service.delete_user(session=session, current_user=current_user, admin=admin, redis=redis)
    return {'success': True, 'message': 'User was deleted'}


#-------------Work with vacancies-------------
@router.get('/vacancies')
async def get_vacancies(session: session_dep, limit: int = 10, offset: int = 0, admin: User = Depends(check_admin)):

    vacancies_info = await admin_service.get_vacancies(session=session, limit=limit, offset=offset, admin=admin)
    return {**vacancies_info}


@router.patch('/vacancies/{vacancy_id}')
async def update_vacancy(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), data: EditVacancy = Depends(), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_service.update_vacancy(session=session, current_vacancy=current_vacancy, data=data, admin=admin, redis=redis)
    return {'success': True, 'message': 'Vacancy was edited'}


@router.delete('/vacancies/{vacancy_id}')
async def delete_vacancy(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_service.delete_vacancy(session=session, current_vacancy=current_vacancy, admin=admin, redis=redis)
    return {'success': True, 'message': 'Vacancy was deleted'}


#-------------Work with resumes-------------
@router.get('/resumes')
async def get_resumes(session: session_dep, limit: int = 10, offset: int = 0, admin: User = Depends(check_admin)):

    resumes_info = await admin_service.get_resumes(session=session, limit=limit, offset=offset, admin=admin)
    return {**resumes_info}


@router.patch('/resumes/{resume_id}')
async def update_resume(session: session_dep, current_resume: Resume = Depends(check_resume), data: EditResume = Depends(), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_service.update_resume(session=session, current_resume=current_resume, data=data, admin=admin, redis=redis)
    return {'success': True, 'message': 'Resume was edited'}


@router.delete('/resumes/{resume_id}')
async def delete_resume(session: session_dep, current_resume: Resume = Depends(check_resume), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_service.delete_resume(session=session, current_resume=current_resume, admin=admin, redis=redis)
    return {'success': True, 'message': 'Resume was deleted'}


#-------------Work with responses-------------
@router.get('/responses')
async def get_responses(session: session_dep, limit: int = 10, offset: int = 0, admin: User = Depends(check_admin)):

    responses_info = await admin_service.get_responses(session=session, limit=limit, offset=offset, admin=admin)    
    return {**responses_info}


@router.delete('/responses/{response_id}')
async def delete_response(session: session_dep, current_response: Response = Depends(check_response), admin: User = Depends(check_admin)):

    await admin_service.delete_response(session=session, current_response=current_response, admin=admin)
    return {'success': True, 'message': 'Response was deleted'}
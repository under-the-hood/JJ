from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from redis.asyncio import Redis

from backend.database.database import session_dep
from backend.dependencies import check_admin, check_vacancy, check_resume, check_user_for_edit_by_admin
from backend.models.response import Response
from backend.models.user import User, Role
from backend.models.vacancy import Vacancy
from backend.models.resume import Resume
from backend.schemas.admin import EditUserNameByAdmin, UpdateUserRoleByAdmin
from backend.schemas.vacancy import EditVacancy
from backend.schemas.resume import EditResume
from backend.services.admin import get_all_users, edit_user_name, update_user_role, delete_user_by_admin, edit_vacancy_by_admin, get_all_vacancies, delete_vacancy_by_admin, edit_resume_by_admin, get_all_resumes, delete_resume_by_admin, get_all_responses, delete_response_by_admin
from backend.database.redis_database import get_redis


router = APIRouter()


#-------------Work with users-------------
@router.get('/admin/get_users', tags=['Admin'])
async def get_users(session: session_dep, limit: int = 10, offset: int = 0, admin: User = Depends(check_admin)):
    
    users_info = await get_all_users(session=session, limit=limit, offset=offset, admin=admin)
    return {**users_info}


@router.put('/admin/edit_user_name/{user_id}', tags=['Admin'])
async def edit_name(data: EditUserNameByAdmin, session: session_dep, current_user: User = Depends(check_user_for_edit_by_admin), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await edit_user_name(data, session, current_user, admin, redis)
    return {'success': True, 'message': 'Users name was edited'}


@router.put('/admin/update_user_role/{user_id}', tags=['Admin'])
async def update_role(session: session_dep, data: UpdateUserRoleByAdmin, current_user: User = Depends(check_user_for_edit_by_admin), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await update_user_role(session, data, current_user, admin, redis)
    return {'success': True, 'message': 'Role was updated'}    


@router.delete('/admin/delete_user/{user_id}', tags=['Admin'])
async def delete_user(session: session_dep, current_user: User = Depends(check_user_for_edit_by_admin), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await delete_user_by_admin(session, current_user, admin, redis)
    return {'success': True, 'message': 'User was deleted'}


#-------------Work with vacancies-------------
@router.put('/admin/edit_vacancy/{vacancy_id}', tags=['Admin'])
async def edit_vacancy(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), data: EditVacancy = Depends(), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await edit_vacancy_by_admin(session, current_vacancy, data, admin, redis)
    return {'success': True, 'message': 'Vacancy was edited'}


@router.get('/admin/get_vacancies', tags=['Admin'])
async def get_vacancies(session: session_dep, limit: int = 10, offset: int = 0, admin: User = Depends(check_admin)):

    vacancies_info = await get_all_vacancies(session=session, limit=limit, offset=offset, admin=admin)
    return {**vacancies_info}


@router.delete('/admin/delete_vacancy/{vacancy_id}', tags=['Admin'])
async def delete_vacancy(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await delete_vacancy_by_admin(session, current_vacancy, admin, redis)
    return {'success': True, 'message': 'Vacancy was deleted'}


#-------------Work with resumes-------------
@router.put('/admin/edit_resume/{resume_id}', tags=['Admin'])
async def edit_resume(session: session_dep, current_resume: Resume = Depends(check_resume), data: EditResume = Depends(), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await edit_resume_by_admin(session, current_resume, data, admin, redis)
    return {'success': True, 'message': 'Resume was edited'}


@router.get('/admin/get_resumes', tags=['Admin'])
async def get_resumes(session: session_dep, limit: int = 10, offset: int = 0, admin: User = Depends(check_admin)):

    resumes_info = await get_all_resumes(session=session, limit=limit, offset=offset, admin=admin)
    return {**resumes_info}


@router.delete('/admin/delete_resume/{resume_id}', tags=['Admin'])
async def delete_resume(session: session_dep, current_resume: Resume = Depends(check_resume), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await delete_resume_by_admin(session, current_resume, admin, redis)
    return {'success': True, 'message': 'Resume was deleted'}


#-------------Work with responses-------------
@router.get('/admin/get_responses', tags=['Admin'])
async def get_responses(session: session_dep, limit: int = 10, offset: int = 0, admin: User = Depends(check_admin)):

    responses_info = await get_all_responses(session=session, limit=limit, offset=offset, admin=admin)    
    return {**responses_info}


@router.delete('/admin/delete_response/{response_id}', tags=['Admin'])
async def delete_response(response_id: int, session: session_dep, admin: User = Depends(check_admin)):

    await delete_response_by_admin(response_id, session, admin)
    return {'success': True, 'message': 'Response was deleted'}
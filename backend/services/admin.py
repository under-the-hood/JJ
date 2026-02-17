from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import check_admin, check_vacancy, check_resume, check_user_for_edit_by_admin
from backend.models.response import Response
from backend.models.user import User, Role
from backend.models.vacancy import Vacancy
from backend.models.resume import Resume
from backend.schemas.admin import EditUserNameByAdmin, UpdateUserRoleByAdmin
from backend.schemas.vacancy import EditVacancy
from backend.schemas.resume import EditResume
from backend.dependencies import get_cache_key


#-------------Service for work with users-------------
async def get_all_users(session: AsyncSession, admin: User, limit: int = 10, offset: int = 0):
    query = await session.execute(select(User).limit(limit).offset(offset))
    users = query.scalars().all()

    quantity = await session.scalar(select(func.count(User.id)))

    return {
        'quantity of all users': quantity,
        'users': users
    }


async def edit_user_name(data: EditUserNameByAdmin, session: AsyncSession, current_user: User, admin: User, redis: Redis):

    if current_user.id == admin.id:
        raise HTTPException(status_code=403, detail='You can not edit your own admin account')

    if current_user.role == Role.admin:
        raise HTTPException(status_code=403, detail='You can not edit accounts of other admins')

    current_user.name = data.new_name

    await session.commit()
    await session.refresh(current_user)

    key = get_cache_key("user", current_user.id, "profile")
    await redis.delete(key)


async def update_user_role(session: AsyncSession, data: UpdateUserRoleByAdmin, current_user: User, admin: User, redis: Redis):
    
    if current_user.id == admin.id:
        raise HTTPException(status_code=403, detail='You can not update your own role')

    current_user.role = data.new_role

    await session.commit()
    await session.refresh(current_user)

    key = get_cache_key("user", current_user.id, "profile")
    await redis.delete(key)


async def delete_user_by_admin(session: AsyncSession, current_user: User, admin: User, redis: Redis):

    if current_user.id == admin.id:
        raise HTTPException(status_code=403, detail='You can not delete your own admin account')

    if current_user.role == Role.admin:
        raise HTTPException(status_code=403, detail='You can not delete other admins')

    await session.delete(current_user)
    await session.commit()

    key = get_cache_key("user", current_user.id, "profile")
    await redis.delete(key)


#-------------Service for work with vacancies-------------
async def edit_vacancy_by_admin(session: AsyncSession, current_vacancy: Vacancy, data: EditVacancy, admin: User, redis: Redis):
    
    if data.new_title:
        current_vacancy.title = data.new_title

    if data.new_city:
        current_vacancy.city = data.new_city

    if data.new_compensation:
        current_vacancy.compensation = data.new_compensation

    await session.commit()
    await session.refresh(current_vacancy)
    
    await redis.incr("vacancy_version")


async def get_all_vacancies(session: AsyncSession, admin: User, limit: int = 10, offset: int = 0):
    
    query = await session.execute(select(Vacancy).limit(limit).offset(offset))
    vacancies = query.scalars().all()

    quantity = await session.scalar(select(func.count(Vacancy.id)))

    return {
        'quantity of all vacancies': quantity,
        'vacancies': vacancies
    }


async def delete_vacancy_by_admin(session: AsyncSession, current_vacancy: Vacancy, admin: User, redis: Redis):
    
    await session.delete(current_vacancy)
    await session.commit()
    
    await redis.incr("vacancy_version")



#-------------Service for work with resumes-------------
async def edit_resume_by_admin(session: AsyncSession, current_resume: Resume, data: EditResume, admin: User, redis: Redis):
    
    if data.new_title:
        current_resume.title = data.new_title

    if data.new_about:
        current_resume.about = data.new_about

    if data.new_city:
        current_resume.city = data.new_city

    if data.new_stack:
        current_resume.stack = data.new_stack

    await session.commit()
    await session.refresh(current_resume)

    await redis.incr("resume_version")


async def get_all_resumes(session: AsyncSession, admin: User, limit: int = 10, offset: int = 0):

    query = await session.execute(select(Resume).limit(limit).offset(offset))
    resumes = query.scalars().all()

    quantity = await session.scalar(select(func.count(Resume.id)))

    return {
        'quantity of all resumes': quantity,
        'resumes': resumes
    }


async def delete_resume_by_admin(session: AsyncSession, current_resume: Resume, admin: User, redis: Redis):

    await session.delete(current_resume)
    await session.commit()

    await redis.incr("resume_version")


#-------------Service for work with responses-------------
async def get_all_responses(session: AsyncSession, admin: User, limit: int = 10, offset: int = 0):
    
    query = await session.execute(select(Response).limit(limit).offset(offset))    
    responses = query.scalars().all()
    quantity = await session.scalar(select(func.count(Response.id)))

    return {
        'quantity of all responses': quantity,
        'responses': responses
        }


async def delete_response_by_admin(response_id: int, session: AsyncSession, admin: User):

    query = await session.execute(select(Response).where(Response.id == response_id))
    current_response = query.scalar_one_or_none()

    if not current_response:
        raise HTTPException(status_code=404, detail='Response not found')

    await session.delete(current_response)
    await session.commit()
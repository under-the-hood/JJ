from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from redis.asyncio import Redis

from backend.models.user import User, Role
from backend.models.resume import Resume
from backend.database.database import session_dep
from backend.schemas.resume import CreateResume, EditResume
from backend.dependencies import check_user, check_resume
from backend.database.redis_database import get_redis
from backend.services.resume import create_new_resume, get_all_user_resumes, edit_user_resume, delete_user_resume


router = APIRouter()


@router.post('/resume/create_resume', tags=['Resume'])
async def create_resume(data: CreateResume, session: session_dep, current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    new_resume = await create_new_resume(data, session, current_user, redis)
    return {'success': True, 'message': 'Resume was created', "Resume": new_resume}


@router.get('/resume/get_all_my_resumes', tags=['Resume'])
async def get_all_my_resumes(session: session_dep, current_user: User = Depends(check_user)):

    all_resumes = await get_all_user_resumes(session, current_user)
    return {'success': True, 'Your resumes': all_resumes}


@router.put('/resume/edit_resume/{resume_id}', tags=['Resume'])
async def edit_resume(session: session_dep, current_resume: Resume = Depends(check_resume), data: EditResume = Depends(), current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    await edit_user_resume(session, current_resume, data, current_user, redis)
    return {'success': True, 'message': 'Resume was edited'}


@router.delete('/resume/delete_resume/{resume_id}', tags=['Resume'])
async def delete_resume(session: session_dep, current_resume: Resume = Depends(check_resume), current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    await delete_user_resume(session, current_resume, current_user, redis)
    return {'success': True, 'message': 'Resume was deleted'}
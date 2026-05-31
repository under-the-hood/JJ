from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.models.user import User
from app.backend.models.resume import Resume
from app.backend.database.database import session_dep
from app.backend.schemas.resume import CreateResume, EditResume
from app.backend.dependencies.resume import check_applicant, check_resume_owner
from app.backend.dependencies.user import check_user
from app.backend.database.redis_database import get_redis
from app.backend.services.resume import create_new_resume, get_all_user_resumes, edit_user_resume, delete_user_resume


router = APIRouter()


@router.post('/resume/create_resume', tags=['Resume'])
async def create_resume(session: session_dep, data: CreateResume, current_user: User = Depends(check_applicant), redis: Redis = Depends(get_redis)):

    new_resume = await create_new_resume(session=session, data=data, current_user=current_user, redis=redis)
    return {'success': True, 'message': 'Resume was created', "Resume": new_resume}


@router.get('/resume/get_all_my_resumes', tags=['Resume'])
async def get_all_my_resumes(session: session_dep, current_user: User = Depends(check_user)):

    all_resumes = await get_all_user_resumes(session=session, current_user=current_user)
    return {'success': True, 'Your resumes': all_resumes}


@router.put('/resume/edit_resume/{resume_id}', tags=['Resume'])
async def edit_resume(session: session_dep, current_resume: Resume = Depends(check_resume_owner), data: EditResume = Depends(), redis: Redis = Depends(get_redis)):

    await edit_user_resume(session=session, current_resume=current_resume, data=data, redis=redis)
    return {'success': True, 'message': 'Resume was edited'}


@router.delete('/resume/delete_resume/{resume_id}', tags=['Resume'])
async def delete_resume(session: session_dep, current_resume: Resume = Depends(check_resume_owner), redis: Redis = Depends(get_redis)):

    await delete_user_resume(session=session, current_resume=current_resume, redis=redis)
    return {'success': True, 'message': 'Resume was deleted'}
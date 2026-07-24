from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.models.user import User
from app.backend.models.resume import Resume
from app.backend.database.database import session_dep
from app.backend.schemas.resume import CreateResume, EditResume
from app.backend.dependencies.resume import check_applicant, check_resume_owner
from app.backend.dependencies.user import check_user
from app.backend.database.redis_database import get_redis
import app.backend.services.resume as resume_service


router = APIRouter()


@router.post('/resumes', tags=['Resume'])
async def create_resume(session: session_dep, data: CreateResume, current_user: User = Depends(check_applicant), redis: Redis = Depends(get_redis)):

    new_resume = await resume_service.create_resume(session=session, data=data, current_user=current_user, redis=redis)
    return {'success': True, 'message': 'Resume was created', "Resume": new_resume}


@router.get('/resumes/my', tags=['Resume'])
async def get_my_resumes(session: session_dep, current_user: User = Depends(check_user)):

    all_resumes = await resume_service.get_my_resumes(session=session, current_user=current_user)
    return {'success': True, 'Your resumes': all_resumes}


@router.put('/resumes/{resume_id}', tags=['Resume'])
async def edit_resume(session: session_dep, current_resume: Resume = Depends(check_resume_owner), data: EditResume = Depends(), redis: Redis = Depends(get_redis)):

    await resume_service.edit_resume(session=session, current_resume=current_resume, data=data, redis=redis)
    return {'success': True, 'message': 'Resume was edited'}


@router.delete('/resumes/{resume_id}', tags=['Resume'])
async def delete_resume(session: session_dep, current_resume: Resume = Depends(check_resume_owner), redis: Redis = Depends(get_redis)):

    await resume_service.delete_resume(session=session, current_resume=current_resume, redis=redis)
    return {'success': True, 'message': 'Resume was deleted'}
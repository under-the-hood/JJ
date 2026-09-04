from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.database.redis_database import get_redis
from app.backend.models.user import User
from app.backend.models.resume import Resume
from app.backend.database.database import session_dep
from app.backend.schemas.resume import CreateResume, EditResume
from app.backend.dependencies.resume import check_applicant, check_resume_owner
import app.backend.services.resumes as resume_service
from app.backend.helpers.rate_limiter import rate_limiter_factory


router = APIRouter(prefix="/resumes", tags=["Resume"])

create_resume_limit = rate_limiter_factory("/resumes", 5, 60)

@router.post("", dependencies=[Depends(create_resume_limit)])
async def create_resume(session: session_dep, data: CreateResume, current_user: User = Depends(check_applicant), redis: Redis = Depends(get_redis)):
    new_resume = await resume_service.create_resume(session=session, data=data, current_user=current_user, redis=redis)
    return {'message': 'Resume was created', "resume": new_resume}


@router.get('/my')
async def get_my_resumes(session: session_dep, current_user: User = Depends(check_applicant), redis: Redis = Depends(get_redis)):
    resumes, total, source = await resume_service.get_my_resumes(session=session, current_user=current_user, redis=redis)
    return {"resumes": resumes, "total": total, "source": source}


@router.patch('/{resume_id}')
async def update_resume(session: session_dep, data: EditResume, current_resume: Resume = Depends(check_resume_owner), redis: Redis = Depends(get_redis)):
    await resume_service.update_resume(session=session, data=data, current_resume=current_resume, redis=redis)
    return {'message': 'Resume was edited', "resume": current_resume}


@router.delete('/{resume_id}')
async def delete_resume(session: session_dep, current_resume: Resume = Depends(check_resume_owner), redis: Redis = Depends(get_redis)):
    await resume_service.delete_resume(session=session, current_resume=current_resume, redis=redis)
    return {'message': 'Resume was deleted', "resume_id": current_resume.id}
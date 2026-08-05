from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_admin
from app.backend.dependencies.resume import check_resume
from app.backend.models.user import User
from app.backend.models.resume import Resume
from app.backend.schemas.resume import EditResume
from app.backend.database.redis_database import get_redis
import app.backend.services.admin.resumes as admin_resumes


router = APIRouter(prefix="/resumes", tags=['Admin | Resumes'])

@router.get('')
async def get_resumes(session: session_dep, limit: int = 10, offset: int = 0, admin: User = Depends(check_admin)):

    resumes_info = await admin_resumes.get_resumes(session=session, limit=limit, offset=offset, admin=admin)
    return {**resumes_info}


@router.patch("/{resume_id}")
async def update_resume(session: session_dep, current_resume: Resume = Depends(check_resume), data: EditResume = Depends(), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_resumes.update_resume(session=session, current_resume=current_resume, data=data, admin=admin, redis=redis)
    return {'success': True, 'message': 'Resume was edited'}


@router.delete("/{resume_id}")
async def delete_resume(session: session_dep, current_resume: Resume = Depends(check_resume), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_resumes.delete_resume(session=session, current_resume=current_resume, admin=admin, redis=redis)
    return {'success': True, 'message': 'Resume was deleted'}
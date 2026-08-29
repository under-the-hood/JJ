from fastapi import APIRouter, Depends

from app.backend.models.user import User
from app.backend.models.resume import Resume
from app.backend.database.database import session_dep
from app.backend.schemas.resume import CreateResume, EditResume
from app.backend.dependencies.resume import check_applicant, check_resume_owner
from app.backend.dependencies.user import check_user
import app.backend.services.resumes as resume_service
from app.backend.helpers.rate_limiter import rate_limiter_factory


router = APIRouter(prefix="/resumes", tags=["Resume"])

create_resume_limit = rate_limiter_factory("/resumes", 5, 60)

@router.post("", dependencies=[Depends(create_resume_limit)])
async def create_resume(session: session_dep, data: CreateResume, current_user: User = Depends(check_applicant)):

    new_resume = await resume_service.create_resume(session=session, data=data, current_user=current_user)
    return {'message': 'Resume was created', "resume": new_resume}


@router.get('/my')
async def get_my_resumes(session: session_dep, current_user: User = Depends(check_user)):

    resumes = await resume_service.get_my_resumes(session=session, current_user=current_user)
    return {'resumes': resumes}


@router.patch('/{resume_id}')
async def update_resume(session: session_dep, data: EditResume, current_resume: Resume = Depends(check_resume_owner)):

    await resume_service.update_resume(session=session, data=data, current_resume=current_resume)
    return {'message': 'Resume was edited', "resume": current_resume}


@router.delete('/{resume_id}')
async def delete_resume(session: session_dep, current_resume: Resume = Depends(check_resume_owner)):

    await resume_service.delete_resume(session=session, current_resume=current_resume)
    return {'message': 'Resume was deleted', "resume_id": current_resume.id}
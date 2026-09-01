from fastapi import APIRouter, Depends

from app.backend.helpers.rate_limiter import rate_limiter_factory
from app.backend.database.database import session_dep
from app.backend.schemas.invitations import InvitationSchema
from app.backend.models.user import User
from app.backend.models.resume import Resume
from app.backend.dependencies.vacancy import check_tenant
from app.backend.dependencies.resume import check_resume
import app.backend.services.invitations as invitation_service


router = APIRouter(prefix="/invitation", tags=["Invitation"])

invitation_limit = rate_limiter_factory("/invitation/interview/{resume_id}", 5, 20)

@router.post("/interview/{resume_id}", dependencies=[Depends(invitation_limit)])
async def send_interview_invitation(session: session_dep, data: InvitationSchema, current_resume: Resume = Depends(check_resume), current_user: User = Depends(check_tenant)):
    invitation = await invitation_service.send_interview_invitation(session=session, data=data, current_resume=current_resume, current_user=current_user)
    return {"invitation": invitation}
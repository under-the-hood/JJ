from fastapi import APIRouter, Depends

from app.backend.dependencies.user import check_user
from app.backend.helpers.rate_limiter import rate_limiter_factory
from app.backend.database.database import session_dep
from app.backend.schemas.invitations import InvitationSchema, SearchInvitation, SetStatus
from app.backend.models.user import User
from app.backend.models.resume import Resume
from app.backend.dependencies.resume import check_applicant
from app.backend.dependencies.vacancy import check_tenant, check_tenant_or_admin
from app.backend.dependencies.resume import check_resume
import app.backend.services.invitations as invitation_service
from app.backend.models.invitations import Invitation
from app.backend.dependencies.invitation import check_invitation_owner_or_admin


router = APIRouter(prefix="/invitations", tags=["Invitation"])

invitation_limit = rate_limiter_factory("/invitation/interview/{resume_id}", 5, 20)

@router.post("/interview/{resume_id}", dependencies=[Depends(invitation_limit)])
async def send_interview_invitation(session: session_dep, data: InvitationSchema, current_resume: Resume = Depends(check_resume), current_user: User = Depends(check_tenant)):
    invitation = await invitation_service.send_interview_invitation(session=session, data=data, current_resume=current_resume, current_user=current_user)
    return {"invitation": invitation}


@router.patch("/{invitation_id}/status")
async def set_status(session: session_dep, data: SetStatus, current_invitation: Invitation = Depends(check_invitation_owner_or_admin), current_user: User = Depends(check_applicant)):
    await invitation_service.set_status(session, data, current_invitation, current_user)
    return {"message": "Invitation status was updated"}


delete_invitation_limit = rate_limiter_factory("/invitation/{invitation_id}", 5, 60)

@router.delete("/{invitation_id}", dependencies=[Depends(delete_invitation_limit)])
async def delete_invitation(session: session_dep, current_invitation: Invitation = Depends(check_invitation_owner_or_admin), current_user: User = Depends(check_tenant_or_admin)):
    await invitation_service.delete_invitation(session=session, current_invitation=current_invitation, current_user=current_user)
    return {"message": "Invitation was deleted"}


@router.get("")
async def search_invitations(data: SearchInvitation = Depends(), current_user: User = Depends(check_user)):
    invitations, total = await invitation_service.search_invitations(data=data, current_user=current_user)
    return {"invitations": invitations, "total": total}
from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.backend.database.database import session_dep
from app.backend.models.invitations import Invitation
from app.backend.models.user import User, Role
from app.backend.dependencies.user import check_user


async def check_invitation(session: session_dep, invitation_id: int):
    query = await session.execute(select(Invitation).options(joinedload(Invitation.vacancy), joinedload(Invitation.resume)).where(Invitation.id == invitation_id))
    current_invitation = query.scalar_one_or_none()

    if not current_invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    return current_invitation


async def check_invitation_owner_or_admin(session: session_dep, invitation_id: int, current_user: User = Depends(check_user)):
    current_invitation = await check_invitation(session, invitation_id)

    if current_user.role == Role.admin:
        return current_invitation

    detail = "It's not your invitation"
    if current_user.role == Role.tenant:
        if current_invitation.tenant_id != current_user.id:
            raise HTTPException(status_code=403, detail=detail)
    else:
        if current_invitation.applicant_id != current_user.id:
            raise HTTPException(status_code=403, detail=detail)

    return current_invitation
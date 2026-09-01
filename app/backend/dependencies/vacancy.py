from fastapi import Depends, HTTPException

from app.backend.models.user import User, Role
from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_user
from app.backend.helpers.validator import validate_roles
import app.backend.helpers.vacancy as vacancy_helpers


async def check_tenant(current_user: User = Depends(check_user)):
    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenants can make/update vacancies')

    return current_user

async def check_tenant_or_admin(current_user: User = Depends(check_user)):
    validate_roles(current_user, [Role.tenant, Role.admin], "Only tenants can search vacancies")
    return current_user

async def check_vacancy(session: session_dep, vacancy_id: int):
    current_vacancy = await vacancy_helpers.get_vacancy(session, vacancy_id)
    return current_vacancy

async def check_vacancy_owner(session: session_dep, vacancy_id: int, current_user: User = Depends(check_tenant)):
    current_vacancy = await vacancy_helpers.check_vacancy_owner(session, vacancy_id, current_user.id)
    return current_vacancy
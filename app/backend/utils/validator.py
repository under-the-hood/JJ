from fastapi import HTTPException

from app.backend.models.user import User, Role


def validate_admin_action(current_user: User, current_admin: User):
    if current_user.id == current_admin.id or current_user.role == Role.admin:
        raise HTTPException(status_code=403, detail='You can not edit/delete your/others admin account')

    return current_admin

def validate_user_role(current_user: User, role: Role, error_msg: str):
    if current_user.role != role:
        raise HTTPException(status_code=403, detail=error_msg)
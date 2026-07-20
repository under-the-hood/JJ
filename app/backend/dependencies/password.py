from fastapi import HTTPException, Depends
from sqlalchemy import select

from app.backend.schemas.user import CreateUser, EditPassword, Delete
from app.backend.models.user import User
from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_user
from app.backend.utils.password import verify_passwords_match, verify_password


async def validate_user_registration(data: CreateUser, session: session_dep):
    verify_passwords_match(data.password, data.repeat_password)

    exiting_user = await session.execute(select(User).where(User.email == data.email))

    if exiting_user.scalar_one_or_none():
        raise HTTPException(status_code=409, detail='This email already exists in database')

    return data


async def validate_edit_password(data: EditPassword, current_user: User = Depends(check_user)):
    verify_password(data.old_password, current_user.password)
    verify_passwords_match(data.new_password, data.repeat_new_password)

    return data


async def validate_delete_user(data: Delete, current_user: User = Depends(check_user)):
    verify_password(data.password, hashed_password=current_user.password)

    return data
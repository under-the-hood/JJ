from fastapi import HTTPException, Depends
from sqlalchemy import select

from app.backend.schemas.user import CreateUser, EditPassword, Delete
from app.backend.utils.hash import pwd_context
from app.backend.models.user import User
from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_user


async def validate_user_registration(data: CreateUser, session: session_dep):
    if data.password != data.repeat_password:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    exiting_user = await session.execute(select(User).where(User.email == data.email))

    if exiting_user.scalar_one_or_none():
        raise HTTPException(status_code=409, detail='This email already exists in database')

    return data


async def verify_password(data: EditPassword | Delete, current_user: User = Depends(check_user)):
    
    if hasattr(data, 'old_password'):
        password_to_check = data.old_password
    else:
        password_to_check = data.password

    if not pwd_context.verify(password_to_check, current_user.password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    return data


async def validate_new_password(data: EditPassword = Depends(verify_password)):
    if data.new_password != data.repeat_new_password:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    return data
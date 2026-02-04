from fastapi import APIRouter, HTTPException, Cookie, Response, Depends
from sqlalchemy import select

from backend.database.database import session_dep
from backend.database.hash import hashing_password, pwd_context, security, config
from backend.models.models import UserModel
from backend.schemas.user_schema import CreateUserSchema, LoginUserSchema, EditUserPasswordSchema, EditUserNameSchema, DeleteUserSchema
from backend.dependencies import check_user
from backend.database.limiter import rate_limiter_factory, rate_limiter_factory_by_ip



router = APIRouter()


@router.post('/user/sign_up', tags=['Users'])
async def sign_up(data: CreateUserSchema, session: session_dep):
    
    if data.password != data.repeat_password:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    exiting_user = await session.execute(select(UserModel).where(UserModel.email == data.email))

    if exiting_user.scalar_one_or_none():
        raise HTTPException(status_code=409, detail='This email already exists in database')

    if data.role not in ["tenant", "applicant"]:
        raise HTTPException(status_code=400, detail="Role must be either 'tenant' or 'applicant'")

    new_user = UserModel(
        email = data.email,
        role = data.role,
        name = data.name,
        password = hashing_password(data.password)
    )

    session.add(new_user)
    await session.commit()

    return {'success': True, 'message': 'Account was created'}


login_limit = rate_limiter_factory_by_ip("/user/sign_in", 5, 60)

@router.post('/user/sign_in', tags=['Users'], dependencies=[Depends(login_limit)])
async def sign_in(data: LoginUserSchema, session: session_dep, response: Response):

    query = await session.execute(select(UserModel).where(UserModel.email == data.email))
    current_user = query.scalar_one_or_none()

    error = HTTPException(status_code=401, detail="Incorrect email or password")

    if not current_user:
        raise error

    if not pwd_context.verify(data.password, current_user.password):
        raise error

    token = security.create_access_token(uid=str(current_user.id))
    security.set_access_cookies(token, response=response)

    return {'success': True, 'message': 'Login succesfull', 'token': token}


@router.get('/user/get_info', tags=['Users'])
async def get_info(session: session_dep, current_user: int = Depends(check_user)):

    return {'success': True, 'info': {'id': current_user.id,
                                      'email': current_user.email,
                                      'name': current_user.name,
                                      'role': current_user.role}}


password_limit = rate_limiter_factory("/user/edit_password", 5, 60)

@router.put('/user/edit_password', tags=['Users'], dependencies=[Depends(password_limit)])
async def edit_password(data: EditUserPasswordSchema, session: session_dep, current_user: int = Depends(check_user)):

    if not pwd_context.verify(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    if data.new_password != data.repeat_new_password:
        raise HTTPException(status_code=400, detail="The passwords don't match")

    current_user.password = hashing_password(data.new_password)

    await session.commit()
    await session.refresh(current_user)

    return {'success': 'True', 'message': 'Password was changed'}


@router.put('/user/edit_name', tags=['Users'])
async def edit_name(data: EditUserNameSchema, session: session_dep, current_user: int = Depends(check_user)):

    if not pwd_context.verify(data.password, current_user.password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    current_user.name = data.new_name

    await session.commit()
    await session.refresh(current_user)

    return {'success': True, 'message': 'Name was changed'}


delete_limit = rate_limiter_factory("/user/delete_user", 5, 60)

@router.delete('/user/delete_user', tags=['Users'])
async def delete_user(data: DeleteUserSchema, session: session_dep, current_user: int = Depends(check_user)):

    if not pwd_context.verify(data.password, current_user.password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    await session.delete(current_user)
    await session.commit()

    return {'success': True, 'message': 'Account was deleted'}
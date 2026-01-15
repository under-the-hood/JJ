import pytest
from sqlalchemy import select

from backend.models.models import UserModel
from tests.conftest import ac


@pytest.mark.anyio
async def test_create_user(ac, get_test_session):
    new_user = {
        "email": "user@example.com",
        "name": "artyom",
        "password": "12345678",
        "repeat_password": "12345678",
        "role": "tenant"
    }

    response = await ac.post('/user/sign_up', json=new_user)

    assert response.status_code == 200
    assert response.json()['success'] is True

    query = await get_test_session.execute(select(UserModel).where(UserModel.email == "user@example.com"))
    current_user = query.scalar_one_or_none()

    assert current_user is not None


    login_res = await ac.post('/user/sign_in', json={
        'email': new_user["email"],
        'password': new_user["password"]
    })

    assert login_res.status_code == 200
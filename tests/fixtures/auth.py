from sqlalchemy import select, update

from app.backend.models.user import User


async def get_token(client, role, email, session):
    reg_role = "tenant" if role == "admin" else role

    new_user = {
        "email": email,
        "name": "artyom",
        "password": "12345678",
        "repeat_password": "12345678",
        "role": reg_role
    }

    await client.post("/users/register", json=new_user)

    #Change role in database for admin
    if role == "admin":
        await session.execute(update(User).where(User.email == email).values(role = "admin"))
        await session.flush()

        admin_user = (await session.execute(select(User).where(User.email == email))).scalar_one()
        await session.refresh(admin_user)

    login_response = await client.post('/users/login', json={
        'email': email,
        'password': new_user["password"]
    })
    
    csrf_token = client.cookies.get("csrf_access_token")
    if csrf_token:
        client.headers["X-CSRF-TOKEN"] = csrf_token
    
    return login_response.json().get("token")

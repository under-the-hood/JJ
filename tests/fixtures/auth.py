from sqlalchemy import update, select

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

    await client.post("/users/sign_up", json=new_user)
            
    #Change role in database for admin
    if role == "admin":
        await session.execute(update(User).where(User.email == email).values(role = "admin"))
        await session.flush()
        
        admin_user = (await session.execute(select(User).where(User.email == email))).scalar_one()
        await session.refresh(admin_user)

    login_response = await client.post('/users/sign_in', json={
        'email': email,
        'password': new_user["password"]
    })

    return login_response.json().get("token")
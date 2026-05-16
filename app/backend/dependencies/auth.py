from fastapi import Cookie, HTTPException
from app.backend.utils.auth import security

async def get_user_token(token: str = Cookie()):

    try:
        payload = security._decode_token(token)
        user_id = int(payload.sub)
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail='No token')
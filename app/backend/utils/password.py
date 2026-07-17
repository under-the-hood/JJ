from fastapi import HTTPException

from app.backend.utils.hash import pwd_context


def verify_password(password: str, hashed_password: str):
    if not pwd_context.verify(password, hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect_password")

def verify_passwords_match(password: str, repeat_password: str):
    if password != repeat_password:
        raise HTTPException(status_code=400, detail="Passwords don't match")
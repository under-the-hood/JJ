from authx import AuthXConfig, AuthX
from passlib.context import CryptContext
from datetime import timedelta

from backend.database.config import settings


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hashing_password(password: str):
    return pwd_context.hash(password)


config = AuthXConfig()
config.JWT_SECRET_KEY = settings.KEY_FOR_JWT
config.JWT_ACCESS_COOKIE_NAME = ('token')
config.JWT_TOKEN_LOCATION = ['cookies']
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
config.JWT_COOKIE_CSRF_PROTECT=False
config.JWT_COOKIE_HTTP_ONLY = True
config.JWT_COOKIE_SECURE = False
config.JWT_COOKIE_SAMESITE = "lax"

security = AuthX(config = config)
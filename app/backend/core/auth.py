import os
from datetime import timedelta

from authx import AuthX, AuthXConfig

from app.backend.config import settings

config = AuthXConfig()

config.JWT_SECRET_KEY = settings.KEY_FOR_JWT

config.JWT_ACCESS_COOKIE_NAME = ("access_token")
config.JWT_REFRESH_COOKIE_NAME = ("refresh_token")

config.JWT_TOKEN_LOCATION = ['cookies']

config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=10)
config.JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

config.JWT_COOKIE_CSRF_PROTECT=False
config.JWT_COOKIE_HTTP_ONLY = True
config.JWT_COOKIE_SECURE = False
config.JWT_COOKIE_SAMESITE = "lax"
config.JWT_COOKIE_SECURE = os.getenv("MODE") == "PROD"
config.JWT_COOKIE_CSRF_PROTECT = True

security = AuthX(config = config)

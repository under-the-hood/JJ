import os
from pydantic_settings import BaseSettings


current_dir = os.path.dirname(os.path.abspath(__file__))

class Settings(BaseSettings):
    MODE: str = "DEV"

    DB_HOST: str
    DB_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: int

    KEY_FOR_JWT: str

    @property
    def database(self):
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}'

    @classmethod
    def load_settings(cls):
        mode = os.getenv("MODE", "DEV").upper()
        
        if mode == "TEST":
            env_file = ".test.env"
        elif mode == "PROD":
            env_file = ".prod.env"
        else:
            env_file = ".dev.env"
            
        return cls(_env_file=os.path.join(current_dir, "..", env_file))


settings = Settings.load_settings()
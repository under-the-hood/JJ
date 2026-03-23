from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import settings


engine = create_async_engine(settings.database, future=True, echo=False, poolclass=NullPool)

new_session = async_sessionmaker(autoflush=False, expire_on_commit=False, bind=engine)

async def get_session():
    async with new_session() as session:
        yield session

session_dep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass

#Session for celery
sync_engine = create_engine(settings.database.replace("postgresql+asyncpg", "postgresql"))
celery_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
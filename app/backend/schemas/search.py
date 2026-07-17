from pydantic import Field

from app.backend.schemas.base import Base


class PaginationParams(Base):
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)

class SearchResumes(PaginationParams):
    city: str | None = Field(None, min_length=2, max_length=50, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    stack: str | None = Field(None, min_length=2, max_length=100, pattern=r'^[a-zA-Zа-яА-Я0-9\s\.,!\?\-\(\):;]+$')
    title: str | None = Field(None, min_length=2, max_length=100, pattern=r'^[a-zA-Zа-яА-Я\s]+$')

class SearchVacancies(PaginationParams):
    city: str | None = Field(None, min_length=2, max_length=50, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    title: str | None = Field(None, min_length=2, max_length=100, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    compensation: int | None = Field(None, ge=0, le=10000000)
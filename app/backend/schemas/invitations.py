from pydantic import Field

from app.backend.schemas.base import Base


class InvitationSchema(Base):
    vacancy_id: int
    cover_letter: str = Field(min_length=0, max_length=100, pattern=r'^[a-zA-Zа-яА-Я0-9\s\.,!\?\-\(\):;]+$')
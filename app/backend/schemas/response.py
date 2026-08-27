from pydantic import Field, EmailStr
from enum import Enum

from app.backend.schemas.base import Base
from app.backend.schemas.search import PaginationParams


class Status(str, Enum):
    viewed = 'viewed'
    shortlisted = 'shortlisted'
    interview = 'interview'
    rejected = 'rejected'
    hired = 'hired'

class ResponseSchema(Base):
    resume_id: int
    cover_letter: str = Field(min_length=0, max_length=100, pattern=r'^[a-zA-Zа-яА-Я0-9\s\.,!\?\-\(\):;]+$')

class ApplicantRead(Base):
    id: int
    name: str
    email: EmailStr

class ResumeRead(Base):
    id: int
    title: str
    stack: str

class ResponseStatus(str, Enum):
    send = "send"
    viewed = 'viewed'
    shortlisted = 'shortlisted'
    interview = 'interview'
    rejected = 'rejected'
    hired = 'hired'

class ResponseRead(Base):
    id: int
    cover_letter: str
    status: ResponseStatus
    user: ApplicantRead
    resume: ResumeRead

class SetStatus(Base):
    status: Status

class SearchResponses(PaginationParams):
    title: str | None = Field(default=None, min_length=2, max_length=100, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    stack: str | None = Field(default=None, min_length=2, max_length=100, pattern=r'^[a-zA-Zа-яА-Я0-9\s\.,!\?\-\(\):;]+$')
    status: ResponseStatus | None = Field(default=None)
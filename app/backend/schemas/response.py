from pydantic import Field, EmailStr
from enum import Enum

from app.backend.schemas.base import Base


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

class ResponseRead(Base):
    id: int
    cover_letter: str
    resume: ResumeRead
    user: ApplicantRead

class SetStatus(Base):
    status: Status
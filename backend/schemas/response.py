from pydantic import Field, BaseModel, EmailStr
from enum import Enum


class Status(str, Enum):
    viewed = 'viewed'
    shortlisted = 'shortlisted'
    interview = 'interview'
    rejected = 'rejected'
    hired = 'hired'

class ResponseSchema(BaseModel):
    cover_letter: str = Field(min_length=0, max_length=100, pattern=r'^[a-zA-Zа-яА-Я0-9\s\.,!\?\-\(\):;]+$')

class ApplicantRead(BaseModel):
    id: int
    name: str
    email: EmailStr

class ResumeRead(BaseModel):
    id: int
    title: str
    stack: str

class ResponseRead(BaseModel):
    id: int
    cover_letter: str
    resume: ResumeRead
    user: ApplicantRead

class SetStatus(BaseModel):
    status: Status
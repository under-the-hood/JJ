from pydantic import Field, EmailStr
from enum import Enum

from app.backend.schemas.base import Base


class Role(str, Enum):
    tenant = 'tenant'
    applicant = 'applicant'


class CreateUser(Base):
    email: EmailStr
    password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    repeat_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    role: Role
    name: str = Field(min_length=3, max_length=15, pattern=r'^[a-zA-Zа-яА-Я\s]+$')

class Login(Base):
    email: EmailStr
    password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')

class EditPassword(Base):
    old_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    new_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    repeat_new_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')

class EditName(Base):
    new_name: str = Field(min_length=3, max_length=15, pattern=r'^[a-zA-Zа-яА-Я\s]+$')

class Delete(Base):
    password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
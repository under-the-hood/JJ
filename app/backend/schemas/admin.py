from pydantic import Field
from enum import Enum

from app.backend.schemas.base import Base

class Role(str, Enum):
    tenant = 'tenant'
    applicant = 'applicant' 
    admin = "admin"   

class EditUserNameByAdmin(Base):
    new_name: str = Field(min_length=3, max_length=15, pattern=r'^[a-zA-Zа-яА-Я\s]+$')

class UpdateUserRoleByAdmin(Base):
    new_role: Role
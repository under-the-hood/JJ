from pydantic import Field
from enum import Enum

from app.backend.schemas.base import Base

class Role(str, Enum):
    tenant = 'tenant'
    applicant = 'applicant' 
    admin = "admin"   

class UpdateUser(Base):
    new_name: str | None = Field(default=None, min_length=3, max_length=15, pattern=r"^[a-zA-Zа-яА-Я\s\-']+$")
    new_role: Role | None
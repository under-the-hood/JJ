from pydantic import Field, BaseModel
from enum import Enum

class Role(str, Enum):
    tenant = 'tenant'
    applicant = 'applicant' 
    admin = "admin"   

class EditUserNameByAdmin(BaseModel):
    new_name: str = Field(min_length=3, max_length=15, pattern=r'^[a-zA-Zа-яА-Я\s]+$')

class UpdateUserRoleByAdmin(BaseModel):
    new_role: Role
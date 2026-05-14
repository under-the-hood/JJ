from pydantic import Field, BaseModel


class CreateVacancy(BaseModel):
    title: str = Field(min_length=4, max_length=30, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    compensation: int = Field(ge=0)
    city: str = Field(min_length=2, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s]+$')

class EditVacancy(BaseModel):
    new_title: str | None = Field(default=None, min_length=4, max_length=30, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    new_compensation: int | None = Field(default=None, ge=0)
    new_city: str | None = Field(default=None, min_length=2, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
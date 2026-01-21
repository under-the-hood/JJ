from pydantic import Field, BaseModel


class CreateResumeSchema(BaseModel):
    title: str = Field(min_length=3, max_length=30, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    about: str = Field(min_length=0, max_length=150, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    city: str = Field(min_length=2, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    stack: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Zа-яА-Я0-9\s\.,!\?\-\(\):;]+$')

class EditResumeSchema(BaseModel):
    new_title: str | None = Field(default=None, min_length=2, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    new_about: str | None = Field(default=None, min_length=0, max_length=150, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    new_city: str | None = Field(default=None, min_length=2, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    new_stack: str | None = Field(default=None, min_length=2, max_length=20, pattern=r'^[a-zA-Zа-яА-Я0-9\s\.,!\?\-\(\):;]+$')
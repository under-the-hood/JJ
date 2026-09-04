from pydantic import Field, ConfigDict, TypeAdapter

from app.backend.schemas.base import Base


class CreateVacancy(Base):
    title: str = Field(min_length=4, max_length=30, pattern=r"^[a-zA-Zа-яА-Я0-9\s\.,\-\+#&\(\)/]+$")
    compensation: int = Field(ge=0)
    city: str = Field(min_length=2, max_length=25, pattern=r"^[a-zA-Zа-яА-Я\s\-]+$")

class EditVacancy(Base):
    new_title: str | None = Field(default=None, min_length=4, max_length=30, pattern=r"^[a-zA-Zа-яА-Я0-9\s\.,\-\+#&\(\)/]+$")
    new_compensation: int | None = Field(default=None, ge=0)
    new_city: str | None = Field(default=None, min_length=2, max_length=25, pattern=r"^[a-zA-Zа-яА-Я\s\-]+$")

class VacancyOut(Base):
    id: int
    title: str
    compensation: int
    city: str

    model_config = ConfigDict(from_attributes=True)

vacancy_list_adapter = TypeAdapter(list[VacancyOut])
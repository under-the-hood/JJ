from pydantic import Field

from app.backend.schemas.base import Base
from app.backend.schemas.search import PaginationParams


class InvitationSchema(Base):
    vacancy_id: int
    cover_letter: str = Field(min_length=0, max_length=100, pattern=r"^[a-zA-Zа-яА-Я0-9\s\.,!\?\-\(\):;'@\+#/]+$")


class SearchInvitation(PaginationParams):
    tenant_id: int | None = Field(default=None)
    applicant_id: int | None = Field(default=None)
    vacancy_id: int | None = Field(default=None)
    resume_id: int | None = Field(default=None)
    
    resume_title: str | None = Field(default=None, min_length=2, max_length=100, pattern=r"^[a-zA-Zа-яА-Я0-9\s\.,\-\+#&\(\)/]+$")
    resume_stack: str | None = Field(default=None, min_length=2, max_length=100, pattern=r"^[a-zA-Zа-яА-Я0-9\s\.,!\?\-\(\):;'@\+#/]+$")
    vacancy_title: str | None = Field(default=None, min_length=2, max_length=100, pattern=r"^[a-zA-Zа-яА-Я0-9\s\.,\-\+#&\(\)/]+$")
    cover_letter: str | None = Field(default=None, max_length=100, pattern=r"^[a-zA-Zа-яА-Я0-9\s\.,!\?\-\(\):;'@\+#/]+$")
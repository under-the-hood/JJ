import enum

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.models.base import Base


class ResponseStatus(enum.Enum):
    send = 'send'
    viewed = 'viewed'
    shortlisted = 'shortlisted'
    interview = 'interview'
    rejected = 'rejected'
    hired = 'hired'

class Response(Base):
    __tablename__ = 'responses'
    __table_args__ = (UniqueConstraint("resume_id", "vacancy_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    resume_id: Mapped[int] = mapped_column(ForeignKey('resumes.id', ondelete='CASCADE'))
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancies.id', ondelete='CASCADE'))
    cover_letter: Mapped[str | None] = mapped_column(default=None)
    status: Mapped[ResponseStatus] = mapped_column(default=ResponseStatus.send)

    user = relationship('User', back_populates='responses')
    vacancy = relationship('Vacancy', back_populates='responses')
    resume = relationship('Resume', back_populates='responses')

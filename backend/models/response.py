from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
import enum

from backend.database.database import Base

class ResponseStatus(enum.Enum):
    send = 'send'
    viewed = 'viewed'
    shortlisted = 'shortlisted'
    interview = 'interview'
    rejected = 'rejected'
    hired = 'hired'


class Response(Base):
    __tablename__ = 'responses'

    id: Mapped[int] = mapped_column(primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    resume_id: Mapped[int] = mapped_column(ForeignKey('resumes.id', ondelete='CASCADE'))
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancies.id', ondelete='CASCADE'))
    cover_letter: Mapped[str | None] = mapped_column(default=None)
    status: Mapped[ResponseStatus] = mapped_column(default="send")

    user = relationship('User', back_populates='responses')
    vacancy = relationship('Vacancy', back_populates='responses')
    resume = relationship('Resume', back_populates='responses')

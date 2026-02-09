from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
import enum

from backend.database.database import Base


class Role(enum.Enum):
    tenant = 'tenant'
    applicant = 'applicant'
    admin = 'admin'

class ResponseStatus(enum.Enum):
    send = 'send'
    viewed = 'viewed'
    shortlisted = 'shortlisted'
    interview = 'interview'
    rejected = 'rejected'
    hired = 'hired'

class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    role: Mapped[Role]
    name: Mapped[str]

    vacancy = relationship('VacancyModel', back_populates='user', cascade="all, delete-orphan", passive_deletes=True)
    resume = relationship('ResumeModel', back_populates='user', cascade="all, delete-orphan", passive_deletes=True)
    responses = relationship('ResponseModel', back_populates='user', cascade="all, delete-orphan", passive_deletes=True)


class VacancyModel(Base):
    __tablename__ = 'vacancies'

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    title: Mapped[str]
    compensation: Mapped[int]
    city: Mapped[str]

    user = relationship('UserModel', back_populates='vacancy')
    responses = relationship('ResponseModel', back_populates='vacancy')

    def vacancies_to_dict(self):
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "title": self.title,
            "compensation": self.compensation,
            "city": self.city
        }


class ResumeModel(Base):
    __tablename__ = 'resumes'

    id: Mapped[int] = mapped_column(primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    title: Mapped[str]
    about: Mapped[str]
    stack: Mapped[str]
    city: Mapped[str]


    user = relationship('UserModel', back_populates='resume')
    responses = relationship('ResponseModel', back_populates='resume')

    def resumes_to_dict(self):
        return {
            "id": self.id,
            "applicant_id": self.applicant_id,
            "title": self.title,
            "about": self.about,
            "stack": self.stack,
            "city": self.city
        }


class ResponseModel(Base):
    __tablename__ = 'responses'

    id: Mapped[int] = mapped_column(primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    resume_id: Mapped[int] = mapped_column(ForeignKey('resumes.id', ondelete='CASCADE'))
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancies.id', ondelete='CASCADE'))
    cover_letter: Mapped[str | None] = mapped_column(default=None)
    status: Mapped[ResponseStatus] = mapped_column(default="send")

    user = relationship('UserModel', back_populates='responses')
    vacancy = relationship('VacancyModel', back_populates='responses')
    resume = relationship('ResumeModel', back_populates='responses')

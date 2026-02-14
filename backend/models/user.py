from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from backend.database.database import Base


class Role(enum.Enum):
    tenant = 'tenant'
    applicant = 'applicant'
    admin = 'admin'

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    role: Mapped[Role]
    name: Mapped[str]

    vacancy = relationship('Vacancy', back_populates='user', cascade="all, delete-orphan", passive_deletes=True)
    resume = relationship('Resume', back_populates='user', cascade="all, delete-orphan", passive_deletes=True)
    responses = relationship('Response', back_populates='user', cascade="all, delete-orphan", passive_deletes=True)
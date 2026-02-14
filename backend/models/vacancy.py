from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from backend.database.database import Base

class Vacancy(Base):
    __tablename__ = 'vacancies'

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    title: Mapped[str]
    compensation: Mapped[int]
    city: Mapped[str]

    user = relationship('User', back_populates='vacancy')
    responses = relationship('Response', back_populates='vacancy')

    def vacancies_to_dict(self):
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "title": self.title,
            "compensation": self.compensation,
            "city": self.city
        }
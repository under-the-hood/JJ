from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from backend.database.database import Base


class Resume(Base):
    __tablename__ = 'resumes'

    id: Mapped[int] = mapped_column(primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    title: Mapped[str]
    about: Mapped[str]
    stack: Mapped[str]
    city: Mapped[str]


    user = relationship('User', back_populates='resume')
    responses = relationship('Response', back_populates='resume')

    def resumes_to_dict(self):
        return {
            "id": self.id,
            "applicant_id": self.applicant_id,
            "title": self.title,
            "about": self.about,
            "stack": self.stack,
            "city": self.city
        }
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.backend.models.base import Base

class Mails(Base):
    __tablename__ = "mails"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    subject: Mapped[str]
    body: Mapped[str]

    user = relationship("User", back_populates="mails")
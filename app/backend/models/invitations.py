from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
import enum

from app.backend.models.base import Base


class InvitationStatus(enum.Enum):
    send = "send"
    accepted = "accepted"
    rejected = 'rejected'

class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    tenant_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"))
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.id", ondelete="CASCADE"))
    cover_letter: Mapped[str | None] = mapped_column(default=None)
    status: Mapped[InvitationStatus] = mapped_column(default=InvitationStatus.send)

    applicant = relationship("User", foreign_keys=[applicant_id], back_populates="received_invitations")
    tenant = relationship("User", foreign_keys=[tenant_id], back_populates="sent_invitations")
    vacancy = relationship("Vacancy", back_populates="invitations")
    resume = relationship("Resume", back_populates="invitations")
from app.backend.utils.smtp_email import email_backend
from app.backend.models.mails import Mails
from app.backend.helpers.celery import celery
from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.models.resume import Resume
from app.backend.models.response import Response
from app.backend.database.database import celery_session


@celery.task(name="send_mail_task")
def send_mail_task(mail_id: int):
    with celery_session() as session:
        mail = session.query(Mails).filter(Mails.id == mail_id).first()
        if not mail:
            return "Mail not found"

        recipient = session.query(User).filter(User.id == mail.recipient_id).first()
        if not recipient:
            return "Recipient not found"

        try:
            email_backend.send_email(
                recipient=recipient.email,
                subject=mail.subject,
                body=mail.body
            )
            return f"Email sent to {recipient.email}"
        except Exception as e:
            return f"Error: {e}"
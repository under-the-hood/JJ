import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SmtpEmailBackend:

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        from_email: str,
        use_tls: bool = False,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_email = from_email
        self.use_tls = use_tls
        self.username = username
        self.password = password

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> None:
        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()

            if self.username and self.password:
                server.login(self.username, self.password)

            server.send_message(
                msg=msg,
            )

email_backend = SmtpEmailBackend(
    smtp_server="localhost",
    smtp_port=1025,
    from_email="info@jj.com",
)
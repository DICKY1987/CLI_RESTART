"""Email notification backend."""

from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailNotifier:
    """Send email notifications."""

    def __init__(
        self,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        from_addr: str | None = None,
        to_addrs: list[str] | None = None,
    ):
        """Initialize email notifier."""
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "25"))
        self.from_addr = from_addr or os.getenv("EMAIL_FROM", "noreply@example.com")
        self.to_addrs = to_addrs or os.getenv("EMAIL_TO", "").split(",")

    def send(self, subject: str, body: str, html: bool = False) -> bool:
        """Send email notification."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = ", ".join(self.to_addrs)

        msg.attach(MIMEText(body, "html" if html else "plain"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_workflow_completed(self, workflow_name: str, duration: float) -> bool:
        """Send workflow completion email."""
        return self.send(
            subject=f"Workflow Completed: {workflow_name}",
            body=f"Workflow '{workflow_name}' completed successfully in {duration:.2f}s",
        )

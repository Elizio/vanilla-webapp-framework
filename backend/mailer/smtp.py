"""stdlib ``smtplib`` backend (STARTTLS or SSL). Compatible with Resend."""

from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app

from .backend import EmailBackend, OutboundEmail

logger = logging.getLogger(__name__)

SMTP_TIMEOUT_SECONDS = 10


def _smtp_security() -> str:
    raw = str(current_app.config.get('SMTP_SECURITY') or 'ssl').strip().lower()
    if raw in ('ssl', 'starttls'):
        return raw
    logger.warning('Unknown SMTP_SECURITY %r; using starttls', raw)
    return 'starttls'


class SmtpEmailBackend(EmailBackend):
    """Send mail through SMTP with a 10 s timeout. Never logs secrets."""

    def send(self, message: OutboundEmail) -> None:
        """Deliver ``message`` via SMTP_SSL or STARTTLS.

        Both modes pass ``ssl.create_default_context()`` so the server
        certificate is verified (hostname + default CA store).

        Args:
            message: Fully rendered outbound email.

        Raises:
            OSError: On connection, auth, or send failure.
        """
        host = str(current_app.config.get('SMTP_HOST') or '')
        port = int(current_app.config.get('SMTP_PORT') or 465)
        username = str(current_app.config.get('SMTP_USERNAME') or '')
        password = str(current_app.config.get('SMTP_PASSWORD') or '')
        security = _smtp_security()

        mime = EmailMessage()
        mime['From'] = message.from_addr
        mime['To'] = message.to
        mime['Subject'] = message.subject
        mime.set_content(message.body)
        payload = mime.as_string()

        tls_context = ssl.create_default_context()
        client: smtplib.SMTP
        if security == 'ssl':
            client = smtplib.SMTP_SSL(
                host, port, timeout=SMTP_TIMEOUT_SECONDS, context=tls_context
            )
        else:
            client = smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT_SECONDS)
            client.starttls(context=tls_context)
        try:
            client.login(username, password)
            client.sendmail(message.from_addr, [message.to], payload)
        finally:
            try:
                client.quit()
            except Exception:
                try:
                    client.close()
                except Exception:
                    pass
        logger.info('Sent email purpose=%s', message.purpose)

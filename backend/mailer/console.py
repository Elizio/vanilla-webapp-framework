"""In-memory / log email backend for development and tests."""

from __future__ import annotations

import logging

from flask import current_app

from .backend import EmailBackend, OutboundEmail

logger = logging.getLogger(__name__)

_OUTBOX: list[OutboundEmail] = []


def get_outbox() -> list[OutboundEmail]:
    """Return the process-local console outbox (tests read this).

    Returns:
        The live list of messages sent through the console backend.
    """
    return _OUTBOX


def clear_outbox() -> None:
    """Drop every message in the console outbox."""
    _OUTBOX.clear()


class ConsoleEmailBackend(EmailBackend):
    """Append to an in-memory outbox; never log the body or tokens."""

    def send(self, message: OutboundEmail) -> None:
        """Record ``message`` in the outbox and log metadata only.

        Args:
            message: Fully rendered outbound email.
        """
        _OUTBOX.append(message)
        profile = str(current_app.config.get('APP_PROFILE') or '')
        if profile == 'production':
            logger.info('Sent email purpose=%s', message.purpose)
            return
        logger.info(
            'Console email purpose=%s to=%s subject=%s',
            message.purpose,
            message.to,
            message.subject,
        )

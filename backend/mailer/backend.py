"""Email backend contract and outbound message dataclass."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class OutboundEmail:
    """A plain-text message ready to send.

    Attributes:
        to: Normalized recipient address.
        subject: Subject line (includes ``APP_NAME``).
        body: Plain-text body (includes ``APP_NAME`` and the action link).
        from_addr: RFC 5322 From value (display name + address).
        purpose: ``verify`` or ``reset`` (for logs; never log the body).
    """

    to: str
    subject: str
    body: str
    from_addr: str
    purpose: str


class EmailBackend(ABC):
    """Deliver an :class:`OutboundEmail`."""

    @abstractmethod
    def send(self, message: OutboundEmail) -> None:
        """Send ``message`` or raise on transport failure.

        Args:
            message: Fully rendered outbound email.
        """

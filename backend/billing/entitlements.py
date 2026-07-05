"""Entitlement reads/writes and a feature-gating decorator.

This is the app-owned source of truth for feature access. Feature code should
call :func:`user_has_plan` or use :func:`entitlement_required`, never the
payment provider directly.
"""
from datetime import datetime, timezone
from functools import wraps
from typing import List, Optional

from flask import jsonify

from ..db_repository.database import db_session
from ..models.billing_entitlement import BillingEntitlement

ACTIVE_STATUS = 'active'


def get_entitlements(user_id: int) -> List[BillingEntitlement]:
    """Return all entitlement rows for a user."""
    return (
        BillingEntitlement.query.filter_by(user_id=user_id)
        .order_by(BillingEntitlement.id)
        .all()
    )


def user_has_plan(user_id: int, plan_key: str) -> bool:
    """Return whether the user holds an active, unexpired grant for a plan.

    Args:
        user_id: The user to check.
        plan_key: The application plan id.

    Returns:
        True when an ``active`` entitlement exists and, if it has an expiry,
        that expiry is in the future.
    """
    rows = BillingEntitlement.query.filter_by(
        user_id=user_id, plan_key=plan_key, status=ACTIVE_STATUS
    ).all()
    now = datetime.now(timezone.utc)
    for row in rows:
        if row.current_period_end is None or row.current_period_end > now:
            return True
    return False


def upsert_entitlement(
    *,
    user_id: int,
    plan_key: str,
    provider: str,
    status: str,
    provider_customer_id: Optional[str] = None,
    provider_reference_id: Optional[str] = None,
    current_period_end: Optional[datetime] = None,
) -> BillingEntitlement:
    """Create or update an entitlement for ``(user, plan, provider)``.

    The operation is idempotent on the unique key, so redelivered webhooks do
    not create duplicate grants.
    """
    entitlement = BillingEntitlement.query.filter_by(
        user_id=user_id, plan_key=plan_key, provider=provider
    ).first()

    if entitlement is None:
        entitlement = BillingEntitlement(
            user_id=user_id,
            plan_key=plan_key,
            provider=provider,
        )
        db_session.add(entitlement)

    entitlement.status = status
    if provider_customer_id is not None:
        entitlement.provider_customer_id = provider_customer_id
    if provider_reference_id is not None:
        entitlement.provider_reference_id = provider_reference_id
    entitlement.current_period_end = current_period_end
    entitlement.updated_at = datetime.now(timezone.utc)
    return entitlement


def entitlement_required(plan_key: str):
    """Decorator gating a route on an active entitlement.

    Apply it after ``@token_required`` so ``current_user`` is available::

        @api_bp.route('/api/supporter-badge')
        @token_required
        @entitlement_required('supporter')
        def supporter_badge(current_user):
            ...

    Returns 403 with code ``ENTITLEMENT_REQUIRED`` when the user lacks access.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(current_user, *args, **kwargs):
            if not user_has_plan(current_user.id, plan_key):
                return jsonify({'code': 'ENTITLEMENT_REQUIRED'}), 403
            return f(current_user, *args, **kwargs)

        return wrapper

    return decorator

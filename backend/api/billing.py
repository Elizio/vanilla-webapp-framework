"""Billing API: plans, checkout, status and provider webhooks."""
import requests
from flask import Blueprint, current_app, jsonify, request

from ..billing import service
from ..billing.credits import get_credit_balance_cents
from ..billing.entitlements import get_entitlements
from ..billing.plans import public_plans
from ..billing.providers.base import WebhookVerificationError
from .auth import token_required
from .error_codes import (
    BILLING_NOT_CONFIGURED,
    CHECKOUT_FAILED,
    INVALID_AMOUNT,
    INVALID_PLAN,
    WEBHOOK_INVALID,
    error_response,
)

billing_bp = Blueprint('billing', __name__)


def _serialize_entitlement(entitlement) -> dict:
    """Shape an entitlement row for API responses."""
    period_end = entitlement.current_period_end
    return {
        'plan_key': entitlement.plan_key,
        'status': entitlement.status,
        'provider': entitlement.provider,
        'current_period_end': period_end.isoformat() if period_end else None,
    }


@billing_bp.route('/api/billing/plans', methods=['GET'])
def list_plans():
    """
    List available billing plans.
    ---
    tags:
      - Billing
    responses:
      200:
        description: Plans available for checkout (provider details omitted)
    """
    return jsonify(public_plans())


@billing_bp.route('/api/billing/status', methods=['GET'])
@token_required
def billing_status(current_user):
    """
    Get the current user's entitlements and credit balance.
    ---
    tags:
      - Billing
    security:
      - Bearer: []
    responses:
      200:
        description: Entitlements and credit balance for the user
      401:
        description: Unauthorized
    """
    entitlements = [
        _serialize_entitlement(e) for e in get_entitlements(current_user.id)
    ]
    return jsonify(
        {
            'entitlements': entitlements,
            'credit_balance_cents': get_credit_balance_cents(current_user.id),
        }
    )


@billing_bp.route('/api/billing/checkout', methods=['POST'])
@token_required
def create_checkout(current_user):
    """
    Create a hosted checkout for a plan and return its URL.
    ---
    tags:
      - Billing
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            plan_key:
              type: string
            amount_cents:
              type: integer
          required:
            - plan_key
    responses:
      200:
        description: Checkout URL created
      400:
        description: Invalid plan or amount
      401:
        description: Unauthorized
      503:
        description: Billing is not configured
    """
    data = request.get_json(silent=True) or {}
    plan_key = (data.get('plan_key') or '').strip()
    amount_cents = data.get('amount_cents')

    if not plan_key:
        return error_response(INVALID_PLAN, 400)
    if amount_cents is not None:
        try:
            amount_cents = int(amount_cents)
        except (TypeError, ValueError):
            return error_response(INVALID_AMOUNT, 400)

    try:
        url = service.create_checkout(current_user, plan_key, amount_cents)
    except service.InvalidPlanError:
        return error_response(INVALID_PLAN, 400)
    except service.InvalidAmountError:
        return error_response(INVALID_AMOUNT, 400)
    except service.BillingNotConfiguredError:
        return error_response(BILLING_NOT_CONFIGURED, 503)
    except requests.RequestException as exc:
        current_app.logger.error('Checkout creation failed: %s', exc)
        return error_response(CHECKOUT_FAILED, 502)

    return jsonify({'checkout_url': url})


@billing_bp.route('/api/billing/webhook/lemon-squeezy', methods=['POST'])
def lemon_squeezy_webhook():
    """
    Receive Lemon Squeezy webhook events.
    ---
    tags:
      - Billing
    responses:
      200:
        description: Event accepted (or ignored if unhandled/duplicate)
      400:
        description: Signature verification failed
    """
    raw_body = request.get_data()
    try:
        service.handle_webhook(raw_body, request.headers)
    except WebhookVerificationError:
        return error_response(WEBHOOK_INVALID, 400)
    except Exception as exc:  # noqa: BLE001 - log and report failure
        current_app.logger.error('Webhook processing failed: %s', exc)
        return error_response(WEBHOOK_INVALID, 400)

    return jsonify({'status': 'ok'})

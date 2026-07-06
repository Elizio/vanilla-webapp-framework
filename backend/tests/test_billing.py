"""Tests for the provider-agnostic billing module (Lemon Squeezy adapter)."""
import hashlib
import hmac
import json

from ..db_repository.database import db_session
from ..models.billing_entitlement import BillingEntitlement
from ..models.user import User
from .conftest import csrf_headers, login_user, register_user

LS_API_KEY = 'test-api-key'
LS_STORE_ID = '999'
LS_SECRET = 'whsec_test'
LS_VARIANT = '12345'


def _configure_billing(app):
    """Enable the Lemon Squeezy provider on a test app."""
    app.config['BILLING_PROVIDER'] = 'lemon_squeezy'
    app.config['LEMON_SQUEEZY_API_KEY'] = LS_API_KEY
    app.config['LEMON_SQUEEZY_STORE_ID'] = LS_STORE_ID
    app.config['LEMON_SQUEEZY_WEBHOOK_SECRET'] = LS_SECRET
    app.config['LEMON_SQUEEZY_VARIANT_ID_SUPPORTER'] = LS_VARIANT


def _login_payer(client):
    """Register and log in the billing test user (session cookie on client)."""
    register_user(client, username='payer', password='payersecret')
    login_user(client, username='payer', password='payersecret')


def _payer_id():
    return User.query.filter_by(username='payer').first().id


def _sign(body_bytes):
    return hmac.new(LS_SECRET.encode('utf-8'), body_bytes, hashlib.sha256).hexdigest()


def _order_payload(user_id, order_id='1001', total=1500, variant=LS_VARIANT):
    return {
        'meta': {
            'event_name': 'order_created',
            'custom_data': {'user_id': str(user_id)},
        },
        'data': {
            'type': 'orders',
            'id': str(order_id),
            'attributes': {
                'total': total,
                'customer_id': 555,
                'updated_at': '2026-06-22T10:00:00.000000Z',
                'first_order_item': {'variant_id': int(variant)},
            },
        },
    }


def test_list_plans_is_public(test_client, test_db):
    """Plans endpoint is public and includes the demo supporter plan."""
    resp = test_client.get('/api/billing/plans')
    assert resp.status_code == 200
    plan_keys = [plan['plan_key'] for plan in resp.json]
    assert 'supporter' in plan_keys


def test_status_requires_auth(test_client, test_db):
    """Status endpoint requires a token."""
    resp = test_client.get('/api/billing/status')
    assert resp.status_code == 401


def test_status_empty_for_new_user(test_client, test_db):
    """A fresh user has no entitlements and a zero balance."""
    _login_payer(test_client)
    resp = test_client.get('/api/billing/status')
    assert resp.status_code == 200
    assert resp.json['entitlements'] == []
    assert resp.json['credit_balance_cents'] == 0


def test_checkout_not_configured(test_client, test_db):
    """Checkout reports BILLING_NOT_CONFIGURED when keys are absent."""
    _login_payer(test_client)
    resp = test_client.post(
        '/api/billing/checkout',
        json={'plan_key': 'supporter', 'amount_cents': 1500},
        headers=csrf_headers(test_client),
    )
    assert resp.status_code == 503
    assert resp.json['code'] == 'BILLING_NOT_CONFIGURED'


def test_checkout_invalid_plan(test_app, test_client, test_db):
    """Unknown plan returns INVALID_PLAN."""
    _configure_billing(test_app)
    _login_payer(test_client)
    resp = test_client.post(
        '/api/billing/checkout',
        json={'plan_key': 'does-not-exist', 'amount_cents': 1500},
        headers=csrf_headers(test_client),
    )
    assert resp.status_code == 400
    assert resp.json['code'] == 'INVALID_PLAN'


def test_checkout_amount_below_minimum(test_app, test_client, test_db):
    """A custom amount below the plan minimum returns INVALID_AMOUNT."""
    _configure_billing(test_app)
    _login_payer(test_client)
    resp = test_client.post(
        '/api/billing/checkout',
        json={'plan_key': 'supporter', 'amount_cents': 100},
        headers=csrf_headers(test_client),
    )
    assert resp.status_code == 400
    assert resp.json['code'] == 'INVALID_AMOUNT'


def test_checkout_success(test_app, test_client, test_db, monkeypatch):
    """A configured checkout returns the provider's hosted URL."""
    _configure_billing(test_app)
    _login_payer(test_client)

    captured = {}

    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {'data': {'attributes': {'url': 'https://checkout.example/abc'}}}

    def _fake_post(url, headers=None, data=None, timeout=None):
        captured['url'] = url
        captured['data'] = json.loads(data)
        return _FakeResponse()

    monkeypatch.setattr(
        'backend.billing.providers.lemon_squeezy.requests.post', _fake_post
    )

    resp = test_client.post(
        '/api/billing/checkout',
        json={'plan_key': 'supporter', 'amount_cents': 1500},
        headers=csrf_headers(test_client),
    )
    assert resp.status_code == 200
    assert resp.json['checkout_url'] == 'https://checkout.example/abc'
    assert captured['url'].endswith('/checkouts')
    assert captured['data']['data']['attributes']['custom_price'] == 1500
    relationships = captured['data']['data']['relationships']
    assert relationships['variant']['data']['id'] == LS_VARIANT


def test_webhook_invalid_signature(test_app, test_client, test_db):
    """A bad signature is rejected with WEBHOOK_INVALID."""
    _configure_billing(test_app)
    _login_payer(test_client)
    raw = json.dumps(_order_payload(_payer_id())).encode('utf-8')
    resp = test_client.post(
        '/api/billing/webhook/lemon-squeezy',
        data=raw,
        content_type='application/json',
        headers={'X-Signature': 'deadbeef'},
    )
    assert resp.status_code == 400
    assert resp.json['code'] == 'WEBHOOK_INVALID'


def test_webhook_order_grants_entitlement(test_app, test_client, test_db):
    """A verified order_created grants the supporter entitlement."""
    _configure_billing(test_app)
    _login_payer(test_client)
    uid = _payer_id()
    raw = json.dumps(_order_payload(uid)).encode('utf-8')

    resp = test_client.post(
        '/api/billing/webhook/lemon-squeezy',
        data=raw,
        content_type='application/json',
        headers={'X-Signature': _sign(raw)},
    )
    assert resp.status_code == 200

    rows = BillingEntitlement.query.filter_by(user_id=uid).all()
    assert len(rows) == 1
    assert rows[0].plan_key == 'supporter'
    assert rows[0].status == 'active'

    badge = test_client.get('/api/supporter-badge')
    assert badge.status_code == 200
    assert badge.json['badge'] == 'supporter'


def test_webhook_is_idempotent(test_app, test_client, test_db):
    """Re-delivering the same order does not create a duplicate grant."""
    _configure_billing(test_app)
    _login_payer(test_client)
    uid = _payer_id()
    raw = json.dumps(_order_payload(uid)).encode('utf-8')
    headers = {'X-Signature': _sign(raw)}

    first = test_client.post(
        '/api/billing/webhook/lemon-squeezy',
        data=raw,
        content_type='application/json',
        headers=headers,
    )
    second = test_client.post(
        '/api/billing/webhook/lemon-squeezy',
        data=raw,
        content_type='application/json',
        headers=headers,
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert BillingEntitlement.query.filter_by(user_id=uid).count() == 1


def test_supporter_badge_forbidden_without_entitlement(test_client, test_db):
    """The gated route returns 403 when the user lacks the entitlement."""
    _login_payer(test_client)
    resp = test_client.get('/api/supporter-badge')
    assert resp.status_code == 403
    assert resp.json['code'] == 'ENTITLEMENT_REQUIRED'


def test_credit_helpers(test_client, test_db):
    """Credit top-ups are idempotent and spends reduce the balance."""
    from ..billing import credits

    _login_payer(test_client)
    uid = _payer_id()

    assert credits.get_credit_balance_cents(uid) == 0

    created = credits.add_credits(
        user_id=uid,
        delta_cents=1000,
        provider='lemon_squeezy',
        provider_reference_id='ord-1',
        plan_key='credit_pack_10',
    )
    db_session.commit()
    assert created is True

    duplicate = credits.add_credits(
        user_id=uid,
        delta_cents=1000,
        provider='lemon_squeezy',
        provider_reference_id='ord-1',
    )
    db_session.commit()
    assert duplicate is False
    assert credits.get_credit_balance_cents(uid) == 1000

    assert credits.spend_credits(uid, 400) is True
    db_session.commit()
    assert credits.get_credit_balance_cents(uid) == 600
    assert credits.spend_credits(uid, 10000) is False
    assert credits.get_credit_balance_cents(uid) == 600


def test_status_reports_credit_balance(test_client, test_db):
    """The status endpoint surfaces the credit balance."""
    from ..billing import credits

    _login_payer(test_client)
    uid = _payer_id()
    credits.add_credits(
        user_id=uid,
        delta_cents=2500,
        provider='lemon_squeezy',
        provider_reference_id='ord-2',
    )
    db_session.commit()

    resp = test_client.get('/api/billing/status')
    assert resp.status_code == 200
    assert resp.json['credit_balance_cents'] == 2500

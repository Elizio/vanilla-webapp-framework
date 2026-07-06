"""Billing plan catalog (provider-agnostic).

Plans are defined here, not at the provider. Forking for a commercial product
means adding entries below and wiring provider price/variant ids via env — the
checkout flow, webhook pipeline and UI stay unchanged.
"""
from typing import Dict, List, Optional

PLAN_TYPE_ONE_TIME = 'one_time'
PLAN_TYPE_SUBSCRIPTION = 'subscription'

OUTCOME_ENTITLEMENT = 'entitlement'
OUTCOME_CREDITS = 'credits'
OUTCOME_NONE = 'none'

# Each plan's ``providers`` map references an env var holding the provider id,
# never the id itself — secrets/config stay in the environment.
PLANS: Dict[str, dict] = {
    # Framework demo: a donation (custom amount) that grants an entitlement.
    'supporter': {
        'type': PLAN_TYPE_ONE_TIME,
        'outcome': OUTCOME_ENTITLEMENT,
        'name_key': 'billing.plans.supporter.name',
        'description_key': 'billing.plans.supporter.description',
        'custom_amount': True,
        'min_amount_cents': 500,
        'default_amount_cents': 1000,
        'currency': 'USD',
        'providers': {
            'lemon_squeezy': {'variant_env': 'LEMON_SQUEEZY_VARIANT_ID_SUPPORTER'},
        },
    },
    # Fork templates — copy, uncomment and set the env vars to enable.
    #
    # 'spot_report': {                      # one-off fixed-price purchase
    #     'type': PLAN_TYPE_ONE_TIME,
    #     'outcome': OUTCOME_ENTITLEMENT,
    #     'name_key': 'billing.plans.spot_report.name',
    #     'description_key': 'billing.plans.spot_report.description',
    #     'custom_amount': False,
    #     'amount_cents': 2500,
    #     'currency': 'USD',
    #     'providers': {
    #         'lemon_squeezy': {'variant_env': 'LEMON_SQUEEZY_VARIANT_ID_SPOT'},
    #     },
    # },
    # 'credit_pack_10': {                   # buy in-app budget (credits)
    #     'type': PLAN_TYPE_ONE_TIME,
    #     'outcome': OUTCOME_CREDITS,
    #     'name_key': 'billing.plans.credit_pack_10.name',
    #     'description_key': 'billing.plans.credit_pack_10.description',
    #     'custom_amount': False,
    #     'amount_cents': 1000,
    #     'credits_multiplier': 1,          # credit cents granted per paid cent
    #     'currency': 'USD',
    #     'providers': {
    #         'lemon_squeezy': {'variant_env': 'LEMON_SQUEEZY_VARIANT_ID_CREDIT10'},
    #     },
    # },
    # 'pro_monthly': {                      # recurring subscription
    #     'type': PLAN_TYPE_SUBSCRIPTION,
    #     'outcome': OUTCOME_ENTITLEMENT,
    #     'name_key': 'billing.plans.pro_monthly.name',
    #     'description_key': 'billing.plans.pro_monthly.description',
    #     'custom_amount': False,
    #     'amount_cents': 900,
    #     'currency': 'USD',
    #     'providers': {
    #         'lemon_squeezy': {'variant_env': 'LEMON_SQUEEZY_VARIANT_ID_PRO'},
    #     },
    # },
}


def get_plan(plan_key: str) -> Optional[dict]:
    """Return the plan definition for ``plan_key`` or ``None``."""
    return PLANS.get(plan_key)


def public_plans() -> List[dict]:
    """Return plans shaped for the frontend, omitting provider internals.

    Returns:
        A list of plan dicts safe to expose publicly.
    """
    result: List[dict] = []
    for key, plan in PLANS.items():
        result.append(
            {
                'plan_key': key,
                'type': plan['type'],
                'outcome': plan['outcome'],
                'name_key': plan.get('name_key'),
                'description_key': plan.get('description_key'),
                'custom_amount': plan.get('custom_amount', False),
                'min_amount_cents': plan.get('min_amount_cents'),
                'default_amount_cents': plan.get('default_amount_cents'),
                'amount_cents': plan.get('amount_cents'),
                'currency': plan.get('currency', 'USD'),
            }
        )
    return result

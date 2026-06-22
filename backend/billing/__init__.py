"""Provider-agnostic billing package.

The application talks to :class:`~backend.billing.service.BillingService`,
which delegates provider specifics (checkout creation, webhook verification and
parsing) to a pluggable :class:`~backend.billing.providers.base.BillingProvider`.
Domain state (entitlements and credits) lives in this app's database, so
swapping providers does not touch feature-gating logic.
"""

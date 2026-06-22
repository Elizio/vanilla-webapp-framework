/**
 * Billing page controller: lists plans, shows the user's status, and starts
 * provider-hosted checkout. Provider-agnostic — talks only to /api/billing/*.
 * Bound in templates as ``currentPage.*`` after loadPage().
 * @module controllers/billing
 */
export const billingController = {
    appContext: null,
    isLoading: false,
    error: null,
    plans: [],
    entitlements: [],
    creditBalanceCents: 0,
    amounts: {},
    checkoutPlanKey: null,
    showSuccess: false,

    /** @param {object} appContext - Root spaApp from createSpaApp(). */
    init(appContext) {
        this.appContext = appContext;
        this.isLoading = false;
        this.error = null;
        this.plans = [];
        this.entitlements = [];
        this.creditBalanceCents = 0;
        this.amounts = {};
        this.checkoutPlanKey = null;
        this.showSuccess = new URLSearchParams(window.location.search).get('billing') === 'success';
        if (this.showSuccess) {
            const url = window.location.pathname;
            window.history.replaceState(null, '', url);
        }
        this.loadPlans();
        this.loadStatus();
    },

    /**
     * Format a cents integer as a currency string.
     * @param {number} cents
     * @param {string} [currency]
     * @returns {string}
     */
    formatCents(cents, currency = 'USD') {
        const value = (Number(cents) || 0) / 100;
        try {
            return new Intl.NumberFormat(this.appContext?.locale || 'en', {
                style: 'currency',
                currency,
            }).format(value);
        } catch (err) {
            return `${value.toFixed(2)} ${currency}`;
        }
    },

    /**
     * Resolve a plan display name, falling back to its key.
     * @param {object} plan
     * @returns {string}
     */
    planName(plan) {
        const label = plan.name_key ? this.appContext.t(plan.name_key) : '';
        return label && label !== plan.name_key ? label : plan.plan_key;
    },

    /**
     * Resolve a plan description, or empty string when none is set.
     * @param {object} plan
     * @returns {string}
     */
    planDescription(plan) {
        if (!plan.description_key) {
            return '';
        }
        const text = this.appContext.t(plan.description_key);
        return text === plan.description_key ? '' : text;
    },

    async loadPlans() {
        this.error = null;
        try {
            const response = await fetch('/api/billing/plans');
            if (!response.ok) {
                this.error = this.appContext.t('errors.HTTP_ERROR', { status: response.status });
                return;
            }
            this.plans = await response.json();
            this.plans.forEach((plan) => {
                if (plan.custom_amount) {
                    // Stored in major currency units for the input field.
                    this.amounts[plan.plan_key] = (plan.default_amount_cents ?? 0) / 100;
                }
            });
        } catch (err) {
            this.error = this.appContext.t('errors.FETCH_FAILED');
        }
    },

    async loadStatus() {
        const token = localStorage.getItem('token');
        if (!token) {
            return;
        }
        try {
            const response = await fetch('/api/billing/status', {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (response.status === 401) {
                this.appContext.logout();
                return;
            }
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            this.entitlements = data.entitlements || [];
            this.creditBalanceCents = data.credit_balance_cents || 0;
        } catch (err) {
            /* status is best-effort; ignore transient errors */
        }
    },

    /**
     * Start checkout for a plan and redirect to the hosted checkout URL.
     * @param {object} plan
     */
    async checkout(plan) {
        const token = localStorage.getItem('token');
        if (!token) {
            this.appContext.logout();
            return;
        }

        const body = { plan_key: plan.plan_key };
        if (plan.custom_amount) {
            const cents = Math.round(Number(this.amounts[plan.plan_key]) * 100);
            const minimum = plan.min_amount_cents ?? 0;
            if (!Number.isFinite(cents) || cents < minimum) {
                this.error = this.appContext.t('billing.amountTooLow', {
                    min: this.formatCents(minimum, plan.currency),
                });
                return;
            }
            body.amount_cents = cents;
        }

        this.isLoading = true;
        this.checkoutPlanKey = plan.plan_key;
        this.error = null;
        try {
            const response = await fetch('/api/billing/checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify(body),
            });
            if (!response.ok) {
                const data = await response.json().catch(() => ({}));
                if (data.code === 'BILLING_NOT_CONFIGURED') {
                    this.error = this.appContext.t('billing.notConfigured');
                } else {
                    this.error = this.appContext.t('errors.HTTP_ERROR', { status: response.status });
                }
                return;
            }
            const data = await response.json();
            window.location.href = data.checkout_url;
        } catch (err) {
            this.error = this.appContext.t('errors.FETCH_FAILED');
        } finally {
            this.isLoading = false;
            this.checkoutPlanKey = null;
        }
    },
};

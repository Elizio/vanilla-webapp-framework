# Billing Configuration Documentation — Design Spec

**Date:** 2026-06-22  
**Status:** Approved  
**Scope:** `docs/billing-configuration.md`, README/AGENTS/cursor-rules cross-links, no code changes

## Problem

Billing human setup (Lemon Squeezy dashboard, webhooks, test mode) lives inline in `README.md` → Configure & operate. OAuth already uses a dedicated `docs/oauth-configuration.md` for provider-specific console steps. Billing is asymmetric: README will grow with each provider, while agent code recipes already live in `backend/AGENTS.md`.

## Goals

1. Mirror the OAuth documentation split: README index + env vars; `docs/` for operational depth.
2. Give humans a runnable Lemon Squeezy setup guide with troubleshooting and production checklist.
3. Give agents a clear map: **human setup** → `docs/billing-configuration.md`; **implement adapter** → `backend/AGENTS.md`.
4. Extend documentation policy (AGENTS + `documentation.mdc`) with billing sync triggers.

## Non-goals

- Implementing new billing providers (Stripe adapter remains a stub).
- Legal/tax guidance for PF/MEI/US LLC.
- Duplicating adapter implementation recipes in `docs/`.
- New cursor rule file (`billing-rules.mdc`) — backend AGENTS is sufficient.

## Approaches considered

| Option | Description | Verdict |
|--------|-------------|---------|
| **A. README only** | Keep expanding Configure & operate | Rejected — duplicates OAuth pattern, README bloat |
| **B. Single `docs/billing.md`** | Human + agent content combined | Rejected — violates AGENTS/README boundary (Rule 5.1c) |
| **C. OAuth mirror (recommended)** | `docs/billing-configuration.md` (human) + existing `backend/AGENTS.md` (agent) + README link | **Selected** |

## Documentation roles (billing)

| Layer | Audience | Billing content |
|-------|----------|-----------------|
| `README.md` | Humans | Env var table; one-line link to billing-configuration.md |
| `docs/billing-configuration.md` | Humans | Shared setup, per-provider dashboard steps, troubleshooting, production checklist |
| `backend/AGENTS.md` | Agents | Add/swap provider **adapter** (code); link to billing-configuration.md for dashboard setup |
| Root `AGENTS.md` | Agents | Documentation map entry; README sync triggers for billing |
| `.cursor/rules/documentation.mdc` | Cursor | Configure & operate includes billing; trigger for `docs/billing-configuration.md` |

**Boundary rule:** Dashboard/console steps never go in AGENTS. Adapter recipes never go in `docs/billing-configuration.md`.

## `docs/billing-configuration.md` structure

1. **Overview** — optional; disabled until API key + store id; provider table; API endpoints; link to code (`backend/billing/`, `backend/api/billing.py`).
2. **Shared setup** — env vars, dev vs prod webhook URL pattern, restart Flask, local webhook tunnel (ngrok/cloudflared), verify with `curl /api/billing/plans`.
3. **Checkout flow** — mermaid sequence (browser → checkout → webhook → entitlement/credits).
4. **Lemon Squeezy** — store, product/variant, API key, webhook events (`order_created`, `subscription_*`), `.env` block, test mode.
5. **Stripe** — short “not implemented” stub pointing to `backend/billing/providers/stripe.py` and `backend/AGENTS.md` for future adapter work; no fake dashboard steps.
6. **Troubleshooting** — symptom/cause/fix table (not configured, webhook signature, entitlement missing, tunnel, etc.).
7. **Production checklist** — migrations, build, public webhook URL, verify status endpoint.

## File changes

| File | Change |
|------|--------|
| `docs/billing-configuration.md` | **New** — human how-to |
| `README.md` | Replace inline Lemon Squeezy steps with link; add to Documentation section and project tree |
| `AGENTS.md` | Documentation map row; README sync triggers (billing provider setup, webhook URL, new env vars) |
| `backend/AGENTS.md` | Point human setup to `docs/billing-configuration.md`; step 4 config references billing-configuration.md not README |
| `.cursor/rules/documentation.mdc` | Rule 5.1a: billing in Configure & operate; Rule 5.1b trigger for billing-configuration.md |

## Verification

- Links resolve from README, AGENTS, backend/AGENTS.
- No duplicate Lemon Squeezy steps in README and docs.
- Agent recipe in backend/AGENTS unchanged except cross-links.

## Implementation plan

Single pass, docs-only:

1. Create `docs/billing-configuration.md` (content from current README + oauth-configuration.md structure).
2. Trim README Configure & operate + Documentation section.
3. Update AGENTS.md map and sync triggers.
4. Update backend/AGENTS.md cross-links.
5. Update `documentation.mdc`.

No pytest or frontend build required (documentation-only).

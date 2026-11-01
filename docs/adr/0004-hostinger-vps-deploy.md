# ADR 0004: Deploy to a Hostinger VPS from docker-publish.yml

## Status

Accepted

## Context

The running product is `dsfor.fun/vanilla-webapp-framework` on Hostinger VM `1136636` / Docker project `dsfor`. An unused `workflow_dispatch` stub is not the deploy path.

## Decision

- `.github/workflows/docker-publish.yml` `deploy` job calls `scripts/deploy-hostinger.sh`.
- The script asserts `GET /api/health` returns 200 with `status == "ok"` and `version ==` the merge SHA, then checks `/`. Failure POSTs the previous `VWF_IMAGE`.
- The only deploy secret is `HOSTINGER_API_TOKEN`. Production env lives on the VPS.
- Never push to `master`; every merge auto-deploys.

## Consequences

- PRs must say whether runtime behavior changes.
- Do not edit the deploy job or `scripts/deploy-hostinger.sh` unless the change is explicitly required.
- Historical PaaS notes may remain under `docs/superpowers/**`; operator docs must not claim that host.

# Contributing

Human how-tos: [README.md](README.md). Agent loop and `make` targets: [AGENTS.md](AGENTS.md). Architecture and recipes: [ARCHITECTURE.md](ARCHITECTURE.md).

## One-command loop

```bash
python -m venv .venv
source .venv/bin/activate
make setup
make check
```

`make check` is the local equivalent of CI (`backend`, `frontend`, `lint`) except Docker `make smoke`, which runs inside `build-and-push`. Do not push to `master`.

## Pull requests

Use the [pull request template](.github/pull_request_template.md). One PR per change, targeting `master`. Required checks: `backend`, `frontend`, `build-and-push`, plus `lint`. Keep the branch up to date with `master`.

Say whether runtime behavior changes. Every merge auto-deploys to the Hostinger VPS.

## Issues

Use the bug or feature templates under [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/).

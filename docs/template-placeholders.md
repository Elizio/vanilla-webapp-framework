# Template placeholders

One list of names that `scripts/init-project` / `make init NAME=...` rewrites. After init, this file holds the **new** values so a second run is a no-op and a leftover search for the original template names stays clean.

```
PROJECT_SLUG=vanilla-webapp-framework
PROJECT_TITLE=Vanilla WebApp Framework
FRONTEND_PACKAGE=vanilla-webapp-frontend
IMAGE_NAME=elizio/vanilla-webapp-framework
PUBLIC_HOST=dsfor.fun
APP_SUBPATH=/vanilla-webapp-framework
HOSTINGER_VM=1136636
HOSTINGER_PROJECT=dsfor
GITHUB_OWNER=Elizio
SETUP_AUTHOR=Your Name
SETUP_EMAIL=your.email@example.com
SETUP_URL=https://github.com/yourusername/vanilla-webapp-framework
```

| Key | Meaning |
|-----|---------|
| `PROJECT_SLUG` | Repo / Python package / directory name |
| `PROJECT_TITLE` | Human title in README and docs |
| `FRONTEND_PACKAGE` | `frontend/package.json` `name` |
| `IMAGE_NAME` | GHCR image (`ghcr.io/<IMAGE_NAME>`) |
| `PUBLIC_HOST` | Public hostname |
| `APP_SUBPATH` | Cookie / Vite public prefix (no trailing slash) |
| `HOSTINGER_VM` | VPS id used by `scripts/deploy-hostinger.sh` |
| `HOSTINGER_PROJECT` | Hostinger Docker project name |
| `GITHUB_OWNER` | GitHub user/org (`CODEOWNERS`, advisory URL) |
| `SETUP_AUTHOR` | `setup.py` author |
| `SETUP_EMAIL` | `setup.py` author_email |
| `SETUP_URL` | `setup.py` / docs repo URL |

Init also resets dated plans under `docs/superpowers/` (they belong to this repo's history, not a fork) and deletes `vibe-prompts-examples/temp.txt` if present.

After `make init NAME=demo`, fill `YOUR_GHCR_OWNER`, `YOUR_VM_ID`, `YOUR_PROJECT`, and `YOUR_GITHUB` in the generated values / Hostinger env. Tick **Template repository** on GitHub (a repo setting, not a PR change).

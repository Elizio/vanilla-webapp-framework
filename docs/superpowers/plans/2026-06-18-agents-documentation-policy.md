# AGENTS Documentation Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add layered documentation policy to AGENTS, cursor rules, and README so agents keep human how-to guides and in-code docstrings current.

**Architecture:** Root `AGENTS.md` holds narrative policy and verification steps. New `.cursor/rules/documentation.mdc` enforces minimums. Sub-AGENTS hold language-specific examples. README is restructured into setup / run-by-environment / configure how-tos with drift fixes.

**Tech Stack:** Markdown, Cursor `.mdc` rules, existing Flask/Vite project (no runtime code changes).

**Spec:** [docs/superpowers/specs/2026-06-18-agents-documentation-policy-design.md](../specs/2026-06-18-agents-documentation-policy-design.md)

---

## File map

| File | Action | Responsibility |
|------|--------|----------------|
| `.cursor/rules/documentation.mdc` | Create | Enforceable README how-to + in-code doc minimums |
| `.cursor/rules/project-structure.mdc` | Modify | Rule 4.4 points to documentation.mdc |
| `.cursor/rules/backend-rules.mdc` | Modify | Rule 1.13 Python docstrings + type hints |
| `.cursor/rules/frontend-rules.mdc` | Modify | Rule 2.12 JSDoc on exports |
| `AGENTS.md` | Modify | Documentation policy section + verification checklist |
| `backend/AGENTS.md` | Modify | Python code documentation examples |
| `frontend/AGENTS.md` | Modify | JSDoc code documentation examples |
| `README.md` | Modify | How-to restructure + drift fix |
| `docs/superpowers/specs/2026-06-18-agents-documentation-policy-design.md` | Modify | Status → Approved |

---

### Task 1: Create documentation rule file

**Files:**
- Create: `.cursor/rules/documentation.mdc`

- [ ] **Step 1: Create the rule file**

```markdown
---
description: README how-to maintenance and in-code documentation standards
globs:
alwaysApply: true
---
## **5. Documentation Rules**

See [AGENTS.md](../AGENTS.md) for narrative policy. These rules are enforceable minimums.

### **README how-to maintenance (Rule 5.1)**
- **Rule 5.1a**: `README.md` is the canonical human how-to. Keep these categories accurate and runnable:
  1. **Project setup** — install, `.env` / `.env.example`, database init (`init_db` vs Alembic).
  2. **Run by environment** — development (dual server), production, Docker, testing.
  3. **Configure & operate** — OAuth redirects, logs, Swagger, migrations, troubleshooting.
- **Rule 5.1b**: Before claiming work done, scan your diff against README sync triggers in `AGENTS.md` → Documentation policy. Update matching how-to sections and `.env.example` when env vars change.
- **Rule 5.1c**: Do not copy AGENTS recipes into README. Do not duplicate README prose in AGENTS.

### **In-code documentation (Rule 5.2)**
- **Rule 5.2a**: Every Python module (`backend/**/*.py`) starts with a one-line module docstring.
- **Rule 5.2b**: Public Python functions and classes use Google-style docstrings and type hints on signatures.
- **Rule 5.2c**: Every API route keeps its Flasgger Swagger YAML block (`---`); do not duplicate it in a separate docstring.
- **Rule 5.2d**: Exported JavaScript modules (`frontend/src/**/*.js`) include a file-level JSDoc block; exported functions/objects include `@param` / `@returns` when not self-evident.
- **Rule 5.2e**: Document new and modified code only — add module docs and document public symbols you touch in files you edit. No repo-wide retroactive pass.

### **Anti-patterns (Rule 5.3)**
- Restating the function name in a docstring.
- README-style essays in module docstrings.
- Claiming unimplemented features in README (e.g. DigitalOcean deploy until built).
```

- [ ] **Step 2: Verify file exists**

Run: `test -f .cursor/rules/documentation.mdc && echo OK`  
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add .cursor/rules/documentation.mdc
git commit -m "Add documentation cursor rule for README how-tos and docstrings."
```

---

### Task 2: Update existing cursor rules

**Files:**
- Modify: `.cursor/rules/project-structure.mdc`
- Modify: `.cursor/rules/backend-rules.mdc`
- Modify: `.cursor/rules/frontend-rules.mdc`

- [ ] **Step 1: Update project-structure Rule 4.4**

Replace Rule 4.4 line in `.cursor/rules/project-structure.mdc`:

```markdown
- **Rule 4.4**: Add module docstrings and JSDoc/type hints per [documentation.mdc](documentation.mdc) (Rule 5.2). Type hints on all public Python signatures; JSDoc on exported JS.
```

- [ ] **Step 2: Add backend Rule 1.13**

Append to `.cursor/rules/backend-rules.mdc` after Rule 1.12:

```markdown
- **Rule 1.13**: Module docstring on every `.py` file; Google-style docstrings and type hints on public functions/classes. See [documentation.mdc](documentation.mdc) and `backend/AGENTS.md`.
```

- [ ] **Step 3: Add frontend Rule 2.12**

Append to `.cursor/rules/frontend-rules.mdc` after Rule 2.11:

```markdown
- **Rule 2.12**: File-level JSDoc on exported modules; `@param` / `@returns` on exported functions when not self-evident. See [documentation.mdc](documentation.mdc) and `frontend/AGENTS.md`.
```

- [ ] **Step 4: Commit**

```bash
git add .cursor/rules/project-structure.mdc .cursor/rules/backend-rules.mdc .cursor/rules/frontend-rules.mdc
git commit -m "Link cursor rules to documentation policy."
```

---

### Task 3: Update root AGENTS.md

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Update documentation map table**

Add row after `.cursor/rules/` row:

```markdown
| [.cursor/rules/documentation.mdc](.cursor/rules/documentation.mdc) | README how-to sync + in-code doc enforcement |
```

- [ ] **Step 2: Insert Documentation policy section**

Insert after `## Verification checklist` block (before `## Architecture`):

```markdown
## Documentation policy

Human **how-to guides** live in [README.md](README.md). Agents keep them accurate — do not relocate how-to prose here.

### README how-to categories

| Category | Update when |
|----------|-------------|
| **Project setup** | Install steps, env vars, database init/migrations change |
| **Run by environment** | Dev, production, Docker, or test run commands change |
| **Configure & operate** | OAuth, logs, Swagger, Alembic, CI, or troubleshooting steps change |

### README sync triggers

| Trigger | README section |
|---------|----------------|
| New env var or config | Project setup → Environment Variables; update `.env.example` |
| Database or migration change | Project setup + Configure & operate (Alembic) |
| Setup / install command change | Project setup |
| Run / start command change | Run by environment |
| New `APP_PROFILE` behavior | Run by environment for that profile |
| User-facing feature or API | Features, Tech Stack |
| Project layout change | Project Structure |
| Deployment / CI change | Run by environment, Deployment |
| OAuth or auth flow change | Project setup + Configure & operate |
| Capability added or removed | Features (remove unimplemented claims) |

**When NOT to update README:** pure refactors, internal-only changes, test-only edits, agent recipes that belong in AGENTS only.

### In-code documentation

| Layer | Standard |
|-------|----------|
| Python | Module docstring; Google-style + type hints on public APIs; Flasgger Swagger on routes |
| JavaScript | File-level JSDoc; `@param` / `@returns` on exports when needed |

Details and examples: [backend/AGENTS.md](backend/AGENTS.md), [frontend/AGENTS.md](frontend/AGENTS.md). Enforceable rules: [.cursor/rules/documentation.mdc](.cursor/rules/documentation.mdc).

**Scope:** document new and modified code; when editing a file, add missing module docs and document public symbols you touch.
```

- [ ] **Step 3: Expand verification checklist**

Append these items to the verification checklist:

```markdown
- [ ] README how-tos checked against diff triggers (setup, run per environment, configure/operate)
- [ ] `.env.example` updated if env vars changed
- [ ] New/modified modules have docstrings; public APIs documented per documentation.mdc
```

- [ ] **Step 4: Add agent principle**

Append to Agent principles list:

```markdown
- README how-tos → update [README.md](README.md) when triggers match; see Documentation policy above
- In-code docs → follow [.cursor/rules/documentation.mdc](.cursor/rules/documentation.mdc)
```

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md
git commit -m "Add documentation policy and README sync triggers to AGENTS.md."
```

---

### Task 4: Update backend/AGENTS.md

**Files:**
- Modify: `backend/AGENTS.md`

- [ ] **Step 1: Add Code documentation section**

Insert before `## See also`:

```markdown
## Code documentation

Enforceable rules: [../.cursor/rules/documentation.mdc](../.cursor/rules/documentation.mdc). API routes also require Swagger (see Swagger section below).

### Module docstring

```python
"""OAuth 2.0 social login via Authlib (Google, Facebook, X/Twitter)."""
```

### Public function (Google-style + type hints)

```python
from backend.models.user import User

def find_or_create_oauth_user(provider: str, subject: str, email: str | None) -> User:
    """Find an existing OAuth user or create a new OAuth-only account.

    Args:
        provider: OAuth provider key (e.g. ``google``).
        subject: Provider-specific user id.
        email: Email from provider profile, if available.

    Returns:
        The matched or newly created User.

    Raises:
        SQLAlchemyError: On database commit failure.
    """
```

### API route handler

Use the Flasgger YAML block only — no separate docstring duplicating Swagger:

```python
@api_bp.route('/api/public', methods=['GET'])
def public_data():
    """
    Get public data
    ---
    tags:
      - Public
    responses:
      200:
        description: Success
    """
    return jsonify({'message': 'Public data'})
```

**Canonical references:** `@backend/api/oauth.py`, `@backend/api/routes.py`
```

- [ ] **Step 2: Commit**

```bash
git add backend/AGENTS.md
git commit -m "Add Python code documentation section to backend AGENTS."
```

---

### Task 5: Update frontend/AGENTS.md

**Files:**
- Modify: `frontend/AGENTS.md`

- [ ] **Step 1: Fix Vite build output path in existing doc**

In the `## Vite configuration` section, replace:

```markdown
- Output: `backend/templates/` (with `emptyOutDir: true`)
- Flask does **not** read this path today — production alignment is pending
```

With:

```markdown
- Output: `backend/static/` (with `emptyOutDir: true`)
- Production Flask serves this directory via SPA fallback (see root AGENTS.md Architecture)
```

Also fix the Development commands section: change `npm run build` comment from `backend/templates/` to `backend/static/`.

- [ ] **Step 2: Add Code documentation section**

Insert before `## See also`:

```markdown
## Code documentation

Enforceable rules: [../.cursor/rules/documentation.mdc](../.cursor/rules/documentation.mdc).

### Module / router

```javascript
/**
 * SPA shell: page registry router, OAuth fragment handler, Alpine root state.
 * @module app
 */

/**
 * Create the Alpine root application object.
 * @returns {object} Alpine x-data root (isLoggedIn, loadPage, controllers, …)
 */
export const createSpaApp = () => { /* … */ };

/**
 * Load a registered page into a DOM target and init Alpine on it.
 * @param {string} elementIdTarget - DOM id of the mount point (e.g. ``view-container``).
 * @param {string} pageKey - Key in ``pages.js`` registry.
 */
loadPage(elementIdTarget, pageKey) { /* … */ }
```

### Page controller

```javascript
/**
 * Landing page: fetches public and protected API samples for demo.
 * Bound in templates as ``currentPage.*`` after loadPage().
 */
export const landingPageController = {
    appContext: null,
    response: null,

    /** @param {object} appContext - Root spaApp from createSpaApp(). */
    init(appContext) {
        this.appContext = appContext;
    },
};
```

**Canonical references:** `@frontend/src/js/app.js`, `@frontend/src/js/controllers/landingpage.js`
```

- [ ] **Step 3: Commit**

```bash
git add frontend/AGENTS.md
git commit -m "Add JSDoc documentation section to frontend AGENTS."
```

---

### Task 6: Restructure README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Fix Features and DevOps DigitalOcean claims**

In `## 🚀 Features` → Development & DevOps, replace:

```markdown
  - DigitalOcean deployment integration
```

With:

```markdown
  - DigitalOcean deployment (planned — not yet automated; see Deployment)
```

In `## 🛠️ Tech Stack` → DevOps, remove `DigitalOcean` line or replace with:

```markdown
- DigitalOcean (planned)
```

- [ ] **Step 2: Fix project structure tree**

Replace the `## 📁 Project Structure` tree with:

```markdown
## 📁 Project Structure

```
vanilla-webapp-framework/
├── backend/
│   ├── api/                    # Flask blueprints
│   ├── config/                 # Application configuration
│   ├── models/                 # SQLAlchemy models
│   ├── db_repository/          # Database layer + Alembic migrations
│   ├── static/                 # Vite production build output
│   ├── tests/                  # Backend tests
│   ├── __init__.py             # create_app() factory
│   ├── app.py                  # Dev entrypoint
│   └── web_routes.py           # SPA fallback + error handlers
├── frontend/
│   ├── src/
│   │   ├── js/                 # Alpine controllers, router, page registry
│   │   ├── styles/             # Tailwind entry CSS
│   │   ├── templates/          # Alpine HTML partials (.hbs)
│   │   └── index.html          # SPA shell
│   ├── tests/                  # Vitest tests
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── docs/                       # Design specs and plans
├── .cursor/rules/              # Cursor coding standards
├── .env.example                # Environment variable template
├── Dockerfile
├── requirements.txt
├── setup.py
└── AGENTS.md                   # Agent guide (AI contributors)
```
```

- [ ] **Step 3: Replace Getting Started with how-to sections**

Replace everything from `## 🚀 Getting Started` through `5. **Testing**` block with:

```markdown
## 🚀 How-To Guides

Copy `.env.example` to `.env` and adjust values before running.

### Setup

1. **Install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   cd frontend && npm install
   ```

2. **Environment variables**

   Create `.env` in the project root (see `.env.example`):

   | Variable | Description |
   | --- | --- |
   | `FLASK_SECRET` | Secret key for Flask sessions and CSRF protection |
   | `JWT_SECRET` | Secret key for JWT token generation and validation |
   | `DATABASE_URI` | Database connection string (SQLite, PostgreSQL, MySQL, etc.) |
   | `PROJECT_FOLDER` | Directory for log files (must exist and be writable) |
   | `APP_PROFILE` | `development`, `testing`, or `production` |
   | `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth (optional) |
   | `FACEBOOK_CLIENT_ID` / `FACEBOOK_CLIENT_SECRET` | Facebook OAuth (optional) |
   | `TWITTER_CLIENT_ID` / `TWITTER_CLIENT_SECRET` | X/Twitter OAuth (optional) |
   | `FRONTEND_URL` | SPA URL after OAuth (default `http://localhost:5173` in dev) |
   | `OAUTH_REDIRECT_BASE` | OAuth callback base URL (default `http://localhost:5173` in dev) |

3. **Database**

   - **Development / testing:** tables are created automatically via `init_db()` when Flask starts (`APP_PROFILE=development` or `testing`).
   - **Production:** run Alembic migrations before serving traffic:

     ```bash
     alembic -c backend/alembic.ini upgrade head
     ```

### Run — development

Use the Vite dev server in the browser (not Flask directly):

```bash
# Terminal 1 — API on :5000
flask run

# Terminal 2 — SPA on :5173
cd frontend && npm run dev
```

Open **http://localhost:5173**. Vite proxies `/api/*` to Flask on port 5000.

API-only work: `flask run` is enough. Swagger UI: http://localhost:5000/docs

### Run — production (local smoke test)

```bash
cd frontend && npm run build
APP_PROFILE=production flask run
```

Open **http://localhost:5000**. Flask serves the Vite build from `backend/static/`.

### Run — Docker

```bash
docker build -t vanilla-webapp .
docker run -p 5000:5000 \
  -e DATABASE_URI=sqlite:////data/app.db \
  -e FLASK_SECRET=your-secret \
  -e JWT_SECRET=your-jwt-secret \
  -e PROJECT_FOLDER=/data \
  -e APP_PROFILE=production \
  vanilla-webapp
```

### Run — testing

```bash
pytest
cd frontend && npm run build && npm run test
```

### Configure & operate

- **OAuth redirect URIs:** register `{OAUTH_REDIRECT_BASE}/api/auth/{provider}/callback` for each provider (e.g. `http://localhost:5173/api/auth/google/callback` in dev so the Vite proxy keeps the session cookie on one origin).
- **Logs:** written to `{PROJECT_FOLDER}/logs/app.log`.
- **API docs:** Swagger UI at `/docs` when Flask is running.
- **Migrations (production):**

  ```bash
  alembic -c backend/alembic.ini revision --autogenerate -m "describe change"
  alembic -c backend/alembic.ini upgrade head
  ```

- **AI contributors:** see [AGENTS.md](AGENTS.md) for agent workflows and verification checklists.
```

- [ ] **Step 4: Update Deployment and Documentation sections**

Replace `## 📦 Deployment` with:

```markdown
## 📦 Deployment

- Docker multi-stage build (see **Run — Docker** above)
- GitHub Actions CI runs `pytest` and frontend build/test
- DigitalOcean deployment automation is **not yet implemented** (see [AGENTS.md](AGENTS.md) follow-ups)
```

Replace `## 📚 Documentation` with:

```markdown
## 📚 Documentation

- **How-to guides:** this README (setup, run, configure)
- **API reference:** Swagger UI at `/docs` when the Flask server is running
- **In-code docs:** Python docstrings + type hints; JavaScript JSDoc (see [AGENTS.md](AGENTS.md) and `.cursor/rules/documentation.mdc`)
- **Agent workflows:** [AGENTS.md](AGENTS.md), [backend/AGENTS.md](backend/AGENTS.md), [frontend/AGENTS.md](frontend/AGENTS.md)
```

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "Restructure README into setup, run, and configure how-to guides."
```

---

### Task 7: Finalize spec and verify

**Files:**
- Modify: `docs/superpowers/specs/2026-06-18-agents-documentation-policy-design.md`

- [ ] **Step 1: Mark spec approved**

Change spec status line to:

```markdown
**Status:** Approved
```

- [ ] **Step 2: Run test suite**

Run: `pytest`  
Expected: all tests pass

Run: `cd frontend && npm run build && npm run test`  
Expected: build succeeds, all Vitest tests pass

- [ ] **Step 3: Manual checklist**

- [ ] README has Setup, Run (dev/prod/Docker/test), Configure & operate sections
- [ ] README env table matches `.env.example` and `AGENTS.md`
- [ ] No unqualified DigitalOcean "integration" claims
- [ ] `documentation.mdc` linked from AGENTS and sub-AGENTS
- [ ] Project structure shows `backend/static/` build output

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-06-18-agents-documentation-policy-design.md docs/superpowers/plans/2026-06-18-agents-documentation-policy.md
git commit -m "Mark documentation policy spec approved; add implementation plan."
```

---

## Spec coverage checklist

| Spec requirement | Task |
|------------------|------|
| Layered policy (AGENTS + rules + sub-AGENTS) | Tasks 1–5 |
| README how-to categories | Task 6 |
| README sync triggers in AGENTS | Task 3 |
| Python docstring level B | Tasks 1, 2, 4 |
| JavaScript JSDoc level B | Tasks 1, 2, 5 |
| One-time README drift fix | Task 6 |
| Verification | Task 7 |

# Vanilla WebApp Framework

A modern, lightweight web application framework that combines Flask backend with a vanilla JavaScript frontend, leveraging Alpine.js and Tailwind CSS for enhanced functionality and styling.

## 🚀 Features

### Backend
- **Flask-based RESTful API**
  - Modular routing with Blueprints
  - SQLAlchemy ORM for database operations
  - JWT authentication for secure endpoints
  - Swagger documentation for API endpoints
  - Comprehensive error handling and logging

### Frontend
- **SPA-like Behavior**
  - Dynamic data loading with Fetch API
  - Handlebars.js templating
  - Alpine.js for lightweight state management
  - Tailwind CSS for utility-first styling
  - Responsive design support
  - Public welcome page for unauthenticated visitors (carousel, affiliate picks, ad slots)
  - Per-fork SEO toolbox (`SEO_MODE`, page metadata, `robots.txt`)

### Development & DevOps
- **Modern Development Workflow**
  - Vite for build optimization
  - Docker support with multi-stage builds
  - GitHub Actions CI/CD pipeline
  - Automated testing with pytest
  - DigitalOcean deployment (planned — not yet automated; see Deployment)

## 🛠️ Tech Stack

### Backend
- Flask
- SQLAlchemy
- JWT Authentication
- Flasgger (Swagger)
- Python 3.x

### Frontend
- Vanilla JavaScript (ES6+)
- Alpine.js
- Handlebars.js
- Tailwind CSS
- Vite

### DevOps
- Docker
- GitHub Actions
- pytest
- DigitalOcean (planned)

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
├── docs/                       # How-tos, design specs, and plans
│   ├── oauth-configuration.md  # OAuth setup (Google, Facebook)
│   └── billing-configuration.md # Billing setup (Lemon Squeezy)
├── .cursor/rules/              # Cursor coding standards
├── .env.example                # Environment variable template
├── Dockerfile
├── requirements.txt
├── setup.py
└── AGENTS.md                   # Agent guide (AI contributors)
```

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
   | `FRONTEND_URL` | SPA URL after OAuth (default `http://localhost:5173` in dev) |
   | `OAUTH_REDIRECT_BASE` | OAuth callback base URL (default `http://localhost:5173` in dev) |
   | `CORS_ORIGINS` | Comma-separated allowed browser origins for credentialed API calls (defaults to `FRONTEND_URL`) |
   | `SEO_MODE` | `auth-first` (default, noindex app pages) or `public-first` (indexable by default); drives frontend meta tags and `/robots.txt`. The public welcome page always uses `index, follow` regardless of mode. |
   | `BILLING_PROVIDER` | Active billing adapter (default `lemon_squeezy`) |
   | `LEMON_SQUEEZY_API_KEY` | Lemon Squeezy API key (billing disabled until set) |
   | `LEMON_SQUEEZY_STORE_ID` | Lemon Squeezy store id used for checkouts |
   | `LEMON_SQUEEZY_WEBHOOK_SECRET` | Secret used to verify webhook signatures |
   | `LEMON_SQUEEZY_VARIANT_ID_SUPPORTER` | Variant id for the demo `supporter` donation plan |

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
cd backend && flask run

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
  -e DATABASE_URI=postgresql://user:pass@host/db \
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

- **OAuth / social login:** optional Google and Facebook. See [docs/oauth-configuration.md](docs/oauth-configuration.md) for provider console setup, redirect URIs, and troubleshooting. Env vars remain in the table above.
- **Billing:** optional Lemon Squeezy demo (donations, spot purchases, credit top-ups). See [docs/billing-configuration.md](docs/billing-configuration.md) for dashboard setup, webhooks, test mode, and troubleshooting. Env vars remain in the table above.
- **Logs:** written to `{PROJECT_FOLDER}/logs/app.log`.
- **Health check:** `GET /api/health` verifies database connectivity (returns 503 when DB is down).
- **API docs:** Swagger UI at `/docs` in development; disabled in production unless `SWAGGER_ENABLED=true`.
- **Migrations (production):**

  ```bash
  alembic -c backend/alembic.ini revision --autogenerate -m "describe change"
  alembic -c backend/alembic.ini upgrade head
  ```

- **AI contributors:** see [AGENTS.md](AGENTS.md) for agent workflows and verification checklists.

## 📝 Development Guidelines

### Backend Development
- Use Flask Blueprints for modular routing
- Follow RESTful conventions
- Implement proper error handling
- Write comprehensive tests
- Document all API endpoints

### Frontend Development
- Use Fetch API for data operations
- Implement responsive design
- Keep Alpine.js logic simple
- Leverage Tailwind utility classes
- Optimize assets with Vite

### Code Standards
- Follow PEP 8 for Python code
- Use ES6+ for JavaScript
- Keep functions modular
- Add proper documentation
- Avoid global variables

## 🔒 Security

- Session auth via httpOnly `auth_token` cookie (JWT signed server-side)
- CSRF double-submit protection on mutating API routes (`GET /api/csrf` + `X-CSRF-Token` header)
- CORS restricted to configured origins with credentials support
- Rate limiting on login and registration (10 requests/minute per IP)
- Input validation and structured error codes (no raw stack traces to clients)
- Bearer token header still supported for API clients and tests

## 📦 Deployment

- Docker multi-stage build (see **Run — Docker** above)
- GitHub Actions CI runs `pytest`, `flake8`, and frontend build/test
- DigitalOcean deploy workflow stub at `.github/workflows/deploy.yml` (fork activates)

## 📚 Documentation

- **How-to guides:** this README (setup, run, configure); [OAuth configuration](docs/oauth-configuration.md) (Google, Facebook); [Billing configuration](docs/billing-configuration.md) (Lemon Squeezy)
- **API reference:** Swagger UI at `/docs` when the Flask server is running
- **In-code docs:** Python docstrings + type hints; JavaScript JSDoc (see [AGENTS.md](AGENTS.md) and `.cursor/rules/documentation.mdc`)
- **Agent workflows:** [AGENTS.md](AGENTS.md), [backend/AGENTS.md](backend/AGENTS.md), [frontend/AGENTS.md](frontend/AGENTS.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow coding standards
4. Add tests for new features
5. Submit a pull request

## 📄 License

[Your License Here]

---

Built with ❤️ using modern web technologies 
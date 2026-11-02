# OAuth Configuration How-To

This guide explains how to enable optional social login for **Google** and **Facebook** in the Vanilla WebApp Framework.

## Overview

Social login is optional. Each provider is enabled only when **both** its `*_CLIENT_ID` and `*_CLIENT_SECRET` are set in `.env`. Providers are implemented in [`backend/api/oauth.py`](../backend/api/oauth.py). The login page shows a generic "sign-in isn't available" message if a user clicks a provider that is not enabled; env var names and the Flask restart stay in this guide (and a `console.warn` for developers).

| Provider key | UI label | Env vars |
|--------------|----------|----------|
| `google` | Google | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| `facebook` | Facebook | `FACEBOOK_CLIENT_ID`, `FACEBOOK_CLIENT_SECRET` |

API endpoints:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/auth/providers` | List enabled providers |
| `GET /api/auth/<provider>/login` | Start OAuth (redirects to provider) |
| `GET /api/auth/<provider>/callback` | Provider callback; sets access + refresh cookies and redirects to the SPA |

### Provider consoles

| Provider | Console URL |
|----------|-------------|
| Google | [https://console.cloud.google.com/](https://console.cloud.google.com/) |
| Facebook | [https://developers.facebook.com/](https://developers.facebook.com/) |

## Shared setup (all providers)

Configure these once in `.env` (see [`.env.example`](../.env.example)):

| Topic | Development | Production |
|-------|-------------|------------|
| `OAUTH_REDIRECT_BASE` | `http://localhost:5173` | Public app URL, **including any subpath** (see [Deploying under a subpath](#deploying-under-a-subpath)) |
| `FRONTEND_URL` | `http://localhost:5173` | Same public URL, including any subpath |
| Redirect URI pattern | `{OAUTH_REDIRECT_BASE}/api/auth/{provider}/callback` | Same |
| Browser origin | `http://localhost:5173` (Vite proxies `/api` to Flask) | Single Flask origin (CORS uses the origin only, not the path) |

**Steps:**

1. Copy `.env.example` to `.env` and add credentials for each provider you want.
2. **Restart Flask** after changing `.env`. OAuth clients register at startup in [`backend/__init__.py`](../backend/__init__.py).
3. In development, run both servers and use **`:5173`** in the browser (not `:5000`):

   ```bash
   # Terminal 1 — API on :5000 (from the repo root)
   flask run

   # Terminal 2 — SPA on :5173
   cd frontend && npm run dev
   ```

4. Verify enabled providers:

   ```bash
   curl http://localhost:5173/api/auth/providers
   ```

   Example response when Google is configured: `["google"]`

### OAuth flow

```mermaid
sequenceDiagram
    participant Browser
    participant Vite as Vite_5173
    participant Flask as Flask_5000
    participant Provider

    Browser->>Vite: Click social login button
    Vite->>Flask: GET /api/auth/provider/login
    Flask->>Provider: Redirect to authorization
    Provider->>Vite: Redirect to /api/auth/provider/callback
    Vite->>Flask: Proxied callback
    Flask->>Provider: Exchange code for token
    Flask->>Browser: Set auth_token + refresh_token cookies; redirect to FRONTEND_URL/?auth=success
```

After a successful login, the callback sets the short-lived httpOnly `auth_token` cookie and a rotating `refresh_token` cookie (OAuth counts as remember-me: 30-day family) and redirects to `FRONTEND_URL/?auth=success`. The SPA (`handleOAuthQuery` in [`frontend/src/js/app.js`](../frontend/src/js/app.js)) reads that query, sets `isLoggedIn`, and later API calls use the cookies. Denied or cancelled consent redirects to `FRONTEND_URL/?auth_error=AUTH_FAILED` (shown as the generic authentication-failed message). Unconfigured providers never start this flow: `GET /api/auth/providers` returns `[]`, login and callback return 404 `PROVIDER_NOT_CONFIGURED`, and the Google/Facebook buttons stay disabled.

### Account linking

When a social login returns an email that already belongs to a local (password) account, the app may attach the OAuth identity to that account instead of creating a second user. `users.email` is **not** unique; this is a best-effort link, not a constraint.

| Provider | When it links by email |
|----------|------------------------|
| **Google** | Only when Google userinfo asserts `email_verified` is `true`. An unverified Google email creates a separate OAuth-only account. |
| **Facebook** | Never. Graph `me?fields=id,name,email` has no verified flag, so Facebook always creates or reuses its own provider account. |

Inactive accounts cannot complete OAuth login: the callback redirects with `auth_error=ACCOUNT_INACTIVE` and does not set a session cookie.

---

## Google

Uses OpenID Connect via Authlib with scopes `openid email profile`.

**Console:** [Google Cloud Console](https://console.cloud.google.com/)

1. Sign in at [https://console.cloud.google.com/](https://console.cloud.google.com/) and create or select a project.
2. Go to **APIs & Services → OAuth consent screen**.
   - Choose **External** (or **Internal** for Google Workspace).
   - Fill in app name, support email, and developer contact.
   - While the app is in **Testing**, only users you add as test users can sign in.
3. Go to **APIs & Services → Credentials → Create credentials → OAuth client ID**.
   - Application type: **Web application**.
4. Under **Authorized redirect URIs**, add:
   - Development: `http://localhost:5173/api/auth/google/callback`
   - Production (this deploy): `https://dsfor.fun/vanilla-webapp-framework/api/auth/google/callback`
   - Production (other hosts): `{OAUTH_REDIRECT_BASE}/api/auth/google/callback`
5. Copy **Client ID** and **Client secret** into `.env`:

   ```env
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

6. Restart Flask and confirm `google` appears in `/api/auth/providers`.

---

## Facebook

**Console:** [Meta for Developers](https://developers.facebook.com/)

This app uses standard **Facebook Login** (not [Facebook Login for Business](https://developers.facebook.com/docs/facebook-login/facebook-login-for-business/)) with permissions `public_profile` and `email`. The callback URL is:

```
{OAUTH_REDIRECT_BASE}/api/auth/facebook/callback
```

### What you need

| Item | Local dev | Production |
|------|-----------|------------|
| Meta **app** (App ID + Secret) | Yes | Yes |
| Business portfolio | No | May be required for App Review |
| App published (Live) | No — keep **Unpublished** | Yes |
| Redirect URI in Meta settings | No — `localhost` is auto-allowed in dev | Yes — register your HTTPS URL |
| App Review for `email` | No | Yes |

You must create a **Meta app** at [developers.facebook.com](https://developers.facebook.com/). A [business portfolio](https://www.facebook.com/business/help/1710077379203657) alone does not provide OAuth credentials.

### Setup

#### 1. Create the app

1. Go to [developers.facebook.com](https://developers.facebook.com/) → **Create App**.
2. Select the use case **Authenticate and request data from users with Facebook Login** ([setup guide](https://developers.facebook.com/docs/facebook-login/create-an-app)).
3. Do **not** choose **Business** app type or **Facebook Login for Business**.

#### 2. Add permissions (do not skip)

1. **Use cases** → **Customize** your Facebook Login use case.
2. Open **Permissions**.
3. Add **`email`**. Keep **`public_profile`** (usually already present).

If `email` is missing, Facebook shows **Invalid Scopes: email** and blocks login.

#### 3. OAuth settings

1. In the same use case, open **Settings**.
2. Under **Client OAuth Settings**, ensure **Client OAuth Login** and **Web OAuth Login** are **On**.
3. **Redirect URIs (development):** while the app is **Unpublished**, Meta allows `http://localhost` automatically. You do **not** need to add `http://localhost:5173/api/auth/facebook/callback` manually. If you do, Meta may show a warning — that is fine; remove the entry or ignore it.
4. **Redirect URIs (production):** add `https://dsfor.fun/vanilla-webapp-framework/api/auth/facebook/callback` (or `{OAUTH_REDIRECT_BASE}/api/auth/facebook/callback` on other hosts) and click **Save changes**.

#### 4. Configure `.env` and restart

Copy **App ID** and **App Secret** from **App settings → Basic**:

```env
FACEBOOK_CLIENT_ID=your-app-id
FACEBOOK_CLIENT_SECRET=your-app-secret
FRONTEND_URL=http://localhost:5173
OAUTH_REDIRECT_BASE=http://localhost:5173
```

Restart Flask, then verify:

```bash
curl http://localhost:5173/api/auth/providers
# ["facebook"]
```

#### 5. Test login

1. Run Flask and Vite; open **http://localhost:5173**.
2. Your Facebook account must have a **role on the app** (Admin, Developer, or Tester) while the app is Unpublished.
3. Click **Facebook** → **Continue** on the consent screen.

An orange banner such as *Submit for login review* is **normal in development**. It does not block you from clicking **Continue** as an app admin/developer.

### Production

Before switching the app to **Live**:

1. Register `https://dsfor.fun/vanilla-webapp-framework/api/auth/facebook/callback` in Facebook Login settings.
2. Complete [App Review](https://developers.facebook.com/docs/development/build-and-test/) for Advanced Access to `email` and `public_profile`.
3. Set `FRONTEND_URL` and `OAUTH_REDIRECT_BASE` as in [Deploying under a subpath](#deploying-under-a-subpath).

---

## Deploying under a subpath

Production for this repository is `https://dsfor.fun/vanilla-webapp-framework`. Keep that subpath on both URL env vars. Leaving them empty or `/` sends the post-login redirect to the domain root (`https://dsfor.fun/?auth=success`) and builds a relative OAuth callback URI.

If a provider's ID or secret is unset (today's live default), that provider stays off: `GET /api/auth/providers` returns `[]`, login and callback return 404 `PROVIDER_NOT_CONFIGURED`, and the login buttons stay disabled. Enabling login is an ops step on the VPS, not a code change.

### (a) Production env vars

Set these on the VPS (never commit values). Example values for this subpath deploy:

| Variable | Example value for `https://dsfor.fun/vanilla-webapp-framework` |
|----------|---------------------------------------------------------------|
| `FRONTEND_URL` | `https://dsfor.fun/vanilla-webapp-framework` |
| `OAUTH_REDIRECT_BASE` | `https://dsfor.fun/vanilla-webapp-framework` |
| `GOOGLE_CLIENT_ID` | from Google Cloud Console (OAuth 2.0 Client ID) |
| `GOOGLE_CLIENT_SECRET` | from Google Cloud Console (OAuth 2.0 Client secret) |
| `FACEBOOK_CLIENT_ID` | from Meta for Developers (App ID) |
| `FACEBOOK_CLIENT_SECRET` | from Meta for Developers (App Secret) |

Restart the app after changing env vars so `register_oauth_clients` picks them up. In production, an enabled provider with an empty `OAUTH_REDIRECT_BASE` logs a warning and does not crash.

### (b) Redirect URIs to register

Redirect base: `https://dsfor.fun/vanilla-webapp-framework`.

| Provider | Authorized redirect URI |
|----------|-------------------------|
| Google | `https://dsfor.fun/vanilla-webapp-framework/api/auth/google/callback` |
| Facebook | `https://dsfor.fun/vanilla-webapp-framework/api/auth/facebook/callback` |

### (c) Other provider-console settings

**Google Cloud Console** (APIs & Services → Credentials → OAuth client ID, application type **Web application**):

- Authorized JavaScript origins: `https://dsfor.fun`
- Authorized redirect URIs: the Google URI in (b)
- OAuth consent screen: External (or Internal for Workspace); while in Testing, only listed test users can sign in

**Meta for Developers** (App settings → Basic, plus Facebook Login → Settings):

- App Domains: `dsfor.fun`
- Site URL: `https://dsfor.fun/vanilla-webapp-framework/`
- Valid OAuth Redirect URIs: the Facebook URI in (b)
- Client OAuth Login: On
- Web OAuth Login: On
- Permissions: `email` and `public_profile` (App Review for Advanced Access before switching the app to Live)

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Social button grayed out or generic "sign-in isn't available" | Missing env vars or Flask not restarted | Set both `*_CLIENT_ID` and `*_CLIENT_SECRET`; restart Flask. The UI stays generic; check the browser console for the env-var hint. |
| `redirect_uri_mismatch` from provider | Redirect URI in provider console does not match | Register exactly `{OAUTH_REDIRECT_BASE}/api/auth/<provider>/callback` |
| Facebook **Invalid Scopes: email** | `email` permission not added to the use case | Use cases → Customize → Permissions → add **email** |
| Facebook localhost URI warning | `localhost` is auto-allowed when the app is Unpublished | Remove the manual entry or ignore; no action needed in dev |
| Facebook **Submit for login review** banner | App not reviewed yet — expected in dev | Click **Continue** if you are an app Admin/Developer/Tester |
| Facebook login blocked for a user | App is Unpublished and user has no app role | Add the user under App settings → Roles, or invite a consumer tester |
| OAuth works on `:5000` but not `:5173` | `OAUTH_REDIRECT_BASE` points to `:5000` in dev | Use `http://localhost:5173` for both `FRONTEND_URL` and `OAUTH_REDIRECT_BASE` |
| `Provider not configured` (404) | Only one of the two env vars is set, or both are unset | Both ID and secret are required per provider; unconfigured is the safe default |
| Startup warning about empty `OAUTH_REDIRECT_BASE` | A provider is enabled in production without a public redirect base | Set `OAUTH_REDIRECT_BASE` to the public app URL including any subpath |
| After login, the browser lands on the domain root | `FRONTEND_URL` is `/` or missing the subpath | Set `FRONTEND_URL` (and `OAUTH_REDIRECT_BASE`) to `https://dsfor.fun/vanilla-webapp-framework` |
| `Authentication failed` after provider redirect | Token exchange or profile fetch failed, or the user denied consent | Lands on the app login page with `auth_error=AUTH_FAILED`, not a 500. Check Flask / `docker logs` (stdout); file logging is opt-in |
| Facebook user has no email after login | User denied email or app lacks Advanced Access in Live mode | Request App Review for `email` before going Live |

---

## Production checklist

1. Run database migrations (OAuth columns are in migration `002`):

   ```bash
   alembic -c backend/alembic.ini upgrade head
   ```

2. Build the frontend and serve from Flask:

   ```bash
   cd frontend && npm run build
   APP_PROFILE=production flask run
   ```

3. Set `FRONTEND_URL` and `OAUTH_REDIRECT_BASE` to the same public app URL, **including any subpath**. For this deploy see [Deploying under a subpath](#deploying-under-a-subpath) (a)(b)(c).

4. Register the exact production redirect URIs from (b) in each provider console, plus the other console settings in (c).

5. For Google: publish the OAuth consent screen or keep test users if still in Testing.

6. For Facebook: complete [App Review](https://developers.facebook.com/docs/development/build-and-test/) for Advanced Access to `email` and `public_profile`, then switch the app to **Live**. A verified business portfolio may be required.

7. Verify: `curl https://dsfor.fun/vanilla-webapp-framework/api/auth/providers` lists your configured providers. Until the VPS env vars in (a) are set, this returns `[]` and the buttons stay disabled.

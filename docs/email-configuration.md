# Email configuration (verification and password reset)

Transactional mail is optional. With no SMTP env vars set, sign-up and login
behave as they do today (no verification gate), and password reset is
unavailable. Nothing fails at startup. This file is the human how-to for
turning sending on. Code layout lives in [`backend/AGENTS.md`](../backend/AGENTS.md)
and [`ARCHITECTURE.md`](../ARCHITECTURE.md).

## Backends

`EMAIL_BACKEND` selects the transport:

| Value | When to use |
|-------|-------------|
| *(empty / unset)* | Default. Email sending off. Safe to deploy. |
| `console` | Development and tests. Messages go to an in-memory outbox (tests) and a metadata-only log line (no body, no tokens). |
| `smtp` | Production. stdlib `smtplib`, 10 s timeout, `ssl` (SMTP_SSL) or `starttls`. |

`smtp` stays disabled (no crash) until **all** of `SMTP_HOST`, `SMTP_USERNAME`,
`SMTP_PASSWORD`, and `EMAIL_FROM` are set **and** `FRONTEND_URL` is an absolute
`http://` or `https://` URL (production SMTP also requires `https://`).

## Environment variables

| Variable | Default | Notes |
|----------|---------|-------|
| `EMAIL_BACKEND` | empty (disabled) | `console` or `smtp` |
| `SMTP_HOST` | empty | Resend: `smtp.resend.com` |
| `SMTP_PORT` | `465` | Resend SSL: `465`. STARTTLS commonly `587`. |
| `SMTP_USERNAME` | empty | Resend: `resend` |
| `SMTP_PASSWORD` | empty | Secret. Resend API key with send-only permission. Never commit it. |
| `SMTP_SECURITY` | `ssl` | `ssl` or `starttls` |
| `EMAIL_FROM` | empty | Envelope/From address, e.g. `no-reply@dsfor.fun` |
| `APP_NAME` | `vanilla-webapp-framework` | From display name, subject, and body |
| `REQUIRE_EMAIL_VERIFIED` | `1` | When sending is on, password login for new unverified accounts returns `403 EMAIL_NOT_VERIFIED` (after a correct password). `0` keeps login working with a banner. |
| `FRONTEND_URL` | existing app URL | Absolute public app URL **including the subpath**. Email links are `{FRONTEND_URL}/?verify_token=…` and `{FRONTEND_URL}/?reset_token=…`. Production: `https://dsfor.fun/vanilla-webapp-framework`. |

## Resend (production on dsfor.fun)

1. Create a Resend account and verify the `dsfor.fun` domain (SPF/DKIM in Hostinger DNS).
2. Create a send-only API key.
3. Set on the VPS (do not put secrets in the repo or the image):

```bash
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.resend.com
SMTP_PORT=465
SMTP_SECURITY=ssl
SMTP_USERNAME=resend
SMTP_PASSWORD=<Resend API key>
EMAIL_FROM=no-reply@dsfor.fun
APP_NAME=vanilla-webapp-framework
FRONTEND_URL=https://dsfor.fun/vanilla-webapp-framework
REQUIRE_EMAIL_VERIFIED=1
```

Hostinger mail is the same SMTP contract (`smtp.hostinger.com`, port `465`, `ssl`).

## Unconfigured mode (safe merge)

Until those vars are set:

- `POST /api/register` still takes username + password and logs the user in.
- Password login is not blocked on `email_verified`.
- `POST /api/auth/password/forgot` and `POST /api/auth/password/reset` return **503** `EMAIL_NOT_CONFIGURED`.
- `GET /api/auth/capabilities` returns `{ "email_configured": false, "password_reset": false, "email_verification": false }` so the SPA hides “Forgot password?”.

## Duplicate-email pre-flight (before migrate)

Revision **010** lowercases emails, keeps the lowest `id` in each duplicate
group, and NULLs the rest, then adds `uq_users_email`. Count duplicates on
the VPS SQLite database first:

```sql
SELECT lower(trim(email)) AS email, COUNT(*) AS n, GROUP_CONCAT(id) AS ids
FROM users
WHERE email IS NOT NULL AND trim(email) != ''
GROUP BY 1
HAVING n > 1;
```

Back up `/data/app.db` before deploy. Existing users get
`verification_exempt=true` and keep logging in.

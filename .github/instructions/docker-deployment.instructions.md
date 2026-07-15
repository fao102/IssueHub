---
applyTo: "backend/Dockerfile*,backend/entry.sh,backend/docker-compose.yml"
---

## Docker & Deployment Guidelines

### Dockerfile (`backend/Dockerfile.dockerfile`)

- Base image: `python:3.11-slim`.
- Key env vars baked in: `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, `PYTHONPATH=/app`, `DJANGO_SETTINGS_MODULE=core.settings`.
- System deps installed: `build-essential`, `libpq-dev` (required for `psycopg2-binary`).
- Entrypoint: `/entry.sh` (copied from `backend/entry.sh`).
- `staticfiles/` directory is created at build time for `collectstatic`.
- **Do not add** a `collectstatic` call to the Dockerfile or `entry.sh` unless WhiteNoise static serving is tested end-to-end first.

### `entry.sh`

Current sequence:
1. `python manage.py migrate --noinput`
2. `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 1`

- Railway injects `$PORT` automatically. Locally it defaults to 8000 if unset.
- Increase `--workers` only after load testing; at 1 worker, memory footprint is minimal on Railway's free tier.

### `docker-compose.yml` (local testing only)

- Starts a `postgres:15` container and the Django web service.
- Uses hardcoded Postgres credentials for local dev only — never use these in production.
- The web service mounts the current directory as a volume (`.:/app`) for live reload during local testing.
- Run with: `cd backend && docker-compose up --build`

### Production Deployment (Railway)

- Triggered by the GitHub Actions webhook in `.github/workflows/deploy.yml`.
- All secrets (`SECRET_KEY`, `DATABASE_URL`, `GEMINI_API_KEY`, `SERP_API_KEY`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `DEBUG`) must be set as Railway environment variables — not in the Dockerfile.
- `SECURE_SSL_REDIRECT=True` and HSTS headers are enabled in production settings. Do not disable them.

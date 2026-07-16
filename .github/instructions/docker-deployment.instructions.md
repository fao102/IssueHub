---
applyTo: "backend/Dockerfile*,backend/entry.sh,backend/docker-compose.yml"
---

## Docker & Deployment Guidelines

### Dockerfile (`backend/Dockerfile`)

- Base image: `python:3.12-slim`.
- Key env vars baked in: `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, `PIP_NO_CACHE_DIR=1`, `PYTHONPATH=/app`, and `DJANGO_SETTINGS_MODULE=config.settings`.
- System deps installed: `libpq-dev` and `gcc` for PostgreSQL driver support.
- The backend source is copied into `/app` with `COPY . /app`.
- `entry.sh` is copied into the image and made executable.
- `staticfiles/` is created at build time.
- The container starts through `CMD ["/app/entry.sh"]`.

### `entry.sh`

Current sequence:
1. `python manage.py migrate --noinput`
2. `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 1`

- In Docker/local runs, set `PORT` to `8000` when needed.
- In deployment, pass `PORT` from the hosting platform environment.
- Keep the startup flow simple: migrations on boot, then Gunicorn serving the Django app.

### `docker-compose.yml` (local testing only)

- Use the backend service from the repo root with `docker compose up --build`.
- The backend build context should be `./backend`, not the repository root.
- `DATABASE_URL` should come from environment variables, not be hardcoded in the Dockerfile.
- When using Neon, keep the database URL in the form `postgresql://<user>:<password>@<host>/<database>?sslmode=require`.
- The frontend is not expected to run in this compose file for the current deployment model.

### Production Deployment (Vercel + Neon)

- Frontend: host the React/Vite app on Vercel.
- Backend: run the Django API in a container-compatible host or deployment target.
- Database: use Neon Postgres and supply the connection string through `DATABASE_URL`.
- Keep all runtime secrets (`SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `FRONTEND_URL`, `DEBUG`, etc.) in environment variables rather than inside the Dockerfile.
- Keep the Django app’s production settings aligned with the existing environment-driven configuration in `config/settings.py`.

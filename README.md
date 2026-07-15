# IssueHub

AI-powered IT Service Management (ITSM) / helpdesk platform. See
[`docs/DESIGN.md`](docs/DESIGN.md) for the full system design and roadmap.

**Stack:** React (Vite) + Bootstrap 5 + Axios · Django + Django REST
Framework + SimpleJWT · PostgreSQL · Docker

## Status

Sprint 1 (Authentication & Foundation) is implemented: registration, login,
JWT access/refresh, email verification and password reset.

## Project layout

```
backend/    Django REST API (accounts, core apps)
frontend/   React + Vite SPA
docs/       Design & architecture documentation
```

## Running locally with Docker (recommended)

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

- Backend API: http://localhost:8000/api
- Frontend: http://localhost:5173
- Django admin: http://localhost:8000/admin

Verification and password-reset emails print to the `backend` container's
logs (`docker compose logs -f backend`) since local dev uses Django's
console email backend.

## Running locally without Docker

### Backend

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements-dev.txt
cp .env.example .env   # defaults to a local sqlite db if DATABASE_URL is unset
python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```

Run the test suite with:

```bash
python manage.py test
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Environment variables

See `backend/.env.example` and `frontend/.env.example` for all configurable
values (secret key, database URL, JWT lifetimes, CORS origins, email
settings, etc).

# IssueHub — Copilot Instructions

## Project Overview

IssueHub is an AI-powered IT Service Management / helpdesk platform. The current implementation is the authentication and foundation sprint: registration, login, JWT access/refresh, email verification, and password reset. The app is a React + Vite SPA with Bootstrap styling on the frontend, and a Django REST Framework backend with SimpleJWT, PostgreSQL, and Docker support.

This repository should be treated as an auth-first product with a clean separation between frontend routing, backend API auth endpoints, and environment-driven configuration.

## Repository Layout

```
IssueHub/
├── backend/                  ← Django REST API
│   ├── accounts/             ← auth flows: register, login, refresh, logout, me,
│   │                          verify email, resend verification, reset password
│   ├── config/               ← Django settings and root URL configuration
│   └── requirements*.txt     ← backend dependencies
├── frontend/                 ← React + Vite SPA
│   ├── src/
│   │   ├── api/              ← axios wrappers and auth API helpers
│   │   ├── components/       ← shared UI and route guards
│   │   ├── context/          ← auth state provider
│   │   ├── pages/            ← login/register/verify/reset/dashboard screens
│   │   └── App.jsx           ← top-level route wiring
└── docs/                     ← architecture and design notes
```

## Tech Stack

- Backend: Python, Django, Django REST Framework, SimpleJWT, PostgreSQL, Docker
- Frontend: React, Vite, Bootstrap 5, Axios, React Router
- Config: environment variables via `python-decouple` in Django and `.env` files in the frontend

## Readme Alignment

The repo README is the authoritative source for local development flow:

- Use Docker Compose for the recommended local workflow.
- Backend APIs are exposed at `http://localhost:8000/api`.
- Frontend runs at `http://localhost:5173`.
- Emails print to the backend container logs during local development; do not assume SMTP is configured.
- When developing without Docker, prefer the backend virtual environment workflow and `python manage.py test` for verification.

## Local Run Commands

### Backend (Docker)

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

### Backend (manual)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Authentication Architecture

IssueHub’s core product behavior is centered on the auth endpoints in `backend/accounts/`:

- `register/`
- `login/`
- `refresh/`
- `logout/`
- `me/`
- `verify-email/`
- `resend-verification/`
- `password-reset/`
- `password-reset/confirm/`

Keep new API work consistent with this pattern rather than inventing a separate auth structure.

## Frontend Routing Expectations

The frontend shell already follows a protected-route layout:

- `/login`
- `/register`
- `/verify-email/:uid/:token`
- `/forgot-password`
- `/reset-password/:uid/:token`
- `/dashboard` behind `ProtectedRoute`

Keep route behavior aligned with `App.jsx`, `AuthContext.jsx`, and the existing pages.

## Environment Variables

### Backend

Use the values defined in `backend/.env.example` and keep them read from environment variables through `config()` in Django settings.

Key values include:

- `SECRET_KEY`
- `DATABASE_URL`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `FRONTEND_URL`
- email settings such as `EMAIL_BACKEND`, `EMAIL_HOST`, `DEFAULT_FROM_EMAIL`
- JWT timing settings such as `ACCESS_TOKEN_LIFETIME_MIN` and `REFRESH_TOKEN_LIFETIME_DAYS`

### Frontend

Use the values defined in `frontend/.env.example`:

- `VITE_API_URL` — backend origin such as `http://localhost:8000`

## Coding Conventions

- Prefer the existing Django app structure: keep auth logic in `backend/accounts/` instead of creating new ad hoc modules.
- Keep business logic in views/serializers; avoid pushing auth-related behavior into unrelated code.
- Follow the current DRF + SimpleJWT pattern for login, refresh, logout, and protected endpoints.
- Keep React components functional, route-driven, and Bootstrap-first.
- Reuse the existing `api` helper module in the frontend rather than hard-coding request URLs in pages.
- Do not commit secrets or `.env` files.
- After any model change, generate and apply migrations with Django management commands.

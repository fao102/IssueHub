---
applyTo: "backend/**/*.py"
---

## Backend Python Guidelines

### Django / DRF Conventions

- Treat the backend as the IssueHub API layer, not as a separate app shell. The main auth implementation lives in `backend/accounts/`.
- Keep all environment reads centralized in `backend/config/settings.py` using `python-decouple` `config()` rather than `os.environ.get`.
- New auth or account-related endpoints should follow the existing `accounts/views.py` / `accounts/serializers.py` / `accounts/urls.py` pattern.
- Use `rest_framework_simplejwt` for token issuance and refresh. Preserve the existing `TokenRefreshView`, `RefreshToken`, and blacklist flow for logout.
- When adding or changing a model field, run Django migrations and keep the app layout consistent with the existing user model and auth flow.

### Auth Flow Expectations

- `RegisterView` should create the user, send a verification email, and return an access/refresh token pair.
- `EmailTokenObtainPairView` is the login entry point and should continue to use the email-based serializer.
- `LogoutView` should blacklist the refresh token and return a `205 RESET CONTENT` response.
- `MeView` should expose the authenticated user record and remain protected behind `IsAuthenticated`.
- Email verification and password-reset flows should remain API-driven and return consistent JSON responses.

### Settings and Environment

- `backend/config/settings.py` is the main settings module. It uses `dj_database_url` and `config()` for environment-based configuration.
- Local development intentionally allows a SQLite fallback when `DATABASE_URL` is unset, matching the README workflow.
- CORS origins should stay configured for the frontend origin at `http://localhost:5173` and any deployed frontend host you intend to support.
- Email is console-backed by default in development. Do not assume production email delivery is configured locally.

### Testing

```bash
cd backend
python manage.py test
```

Use the Django test suite for backend changes and keep new coverage in the relevant app test module rather than adding isolated one-off scripts.

### Project-Specific Notes

- Favor the existing `accounts` app over creating new auth domains or parallel patterns.
- When a change impacts the user model, verification tokens, or password reset flow, keep the frontend route contract in sync.
- Do not remove the current JWT-first default permissions model without updating both the backend and frontend expectations.

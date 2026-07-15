---
applyTo: "frontend/src/**/*.{js,jsx}"
---

## Frontend React / JavaScript Guidelines

### App Structure

- Treat the frontend as a route-driven SPA for IssueHub’s authentication and dashboard experience.
- Keep the routing and auth shell in `frontend/src/App.jsx`, `frontend/src/context/AuthContext.jsx`, and `frontend/src/components/ProtectedRoute.jsx`.
- Use the existing page-level structure in `frontend/src/pages/` for login, registration, email verification, password reset, and dashboard flows.
- Prefer small reusable UI components in `frontend/src/components/` rather than adding ad hoc layout logic directly into page files.

### API Integration

- All backend calls should go through the typed API helpers under `frontend/src/api/` and the shared Axios instance.
- Do not hard-code backend URLs inside pages or components; always read from `import.meta.env.VITE_API_URL` through the API helper layer.
- Keep auth-related endpoints aligned with the backend contract in `frontend/src/api/auth.js`:
  - register
  - login
  - refresh
  - logout
  - me
  - verify email
  - resend verification
  - password reset request
  - password reset confirm

### Authentication UX

- The login session should be stored through the auth context rather than page-local component state.
- Protected routes should remain route-guarded through `ProtectedRoute` instead of manually checking auth in each page.
- Preserve the existing flow where unauthenticated users are redirected to login and authenticated users land on the dashboard.

### Styling

- Prefer Bootstrap 5 utility classes for layout and spacing.
- Keep styling simple and consistent with the existing design patterns in the current pages and components.
- Avoid introducing new CSS frameworks or custom component styling unless the existing Bootstrap utility system cannot support the requirement.

### Environment and Dev Workflow

- The frontend reads runtime variables from `.env` via `import.meta.env`.
- The required variable is `VITE_API_URL`, which should point to the backend origin, such as `http://localhost:8000`.
- Follow the README’s recommended local workflow:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Project-Specific Notes

- IssueHub currently uses a JWT-based auth model. Do not replace it with alternate auth providers unless explicitly requested.
- Keep new pages and components consistent with the route names already used by the backend and the current README-defined local workflow.
- When a backend response contract changes, update the relevant frontend API helper and related page code together.

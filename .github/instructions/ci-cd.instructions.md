---
applyTo: ".github/workflows/**/*.yml"
---

## GitHub Actions Workflow Guidelines

### Current Deployment Workflow (`deploy.yml`)

- Deploys on push to the branch named **`prodcution`** (this is an intentional typo in the existing workflow — do not rename the branch or correct the spelling unless explicitly asked).
- `deploy-backend` triggers a Railway webhook via `curl -X POST ${{ secrets.RAILWAY_WEBHOOK_URL }}`.
- `deploy-frontend` uses `amondnet/vercel-action@v20` with secrets `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`.

### Required Repository Secrets

| Secret | Used by |
|---|---|
| `RAILWAY_WEBHOOK_URL` | Backend deploy |
| `VERCEL_TOKEN` | Frontend deploy |
| `VERCEL_ORG_ID` | Frontend deploy |
| `VERCEL_PROJECT_ID` | Frontend deploy |

### Adding New Workflows

- Place new workflow files in `.github/workflows/`.
- For backend CI (lint/test), run steps inside `backend/` with `working-directory: backend` and activate a Python venv or use `pip install -r requirements.txt`.
- For frontend CI, run steps inside `frontend/` with `working-directory: frontend`; always call `npm install` before `npm run build` or `npm run lint`.
- Use `ubuntu-latest` as the runner unless there is a specific reason to change it.
- Do not add secrets inline — always reference them via `${{ secrets.SECRET_NAME }}`.

### Notes

- The backend has no automated test step in the current CI pipeline. If adding tests, run `python manage.py test` after installing deps.
- The frontend build artifact is handled by Vercel automatically; no manual `npm run build` step is needed in the deploy job.

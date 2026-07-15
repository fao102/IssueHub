---
applyTo: "backend/app/migrations/**/*.py"
---

## Django Migration Guidelines

- **Never hand-edit** generated migration files unless fixing a merge conflict or squashing migrations.
- Always generate migrations with: `python manage.py makemigrations app`
- Apply with: `python manage.py migrate`
- The `entry.sh` container entrypoint runs `migrate --noinput` automatically on every deploy, so new migrations are applied at startup on Railway.
- Migration files must be committed to version control — they are not in `.gitignore`.
- The current migration history:
  - `0001_initial` — creates `OutfitSearch` with `image` and `created_at`.
  - `0002_outfitsearch_color_...` — adds `color`, `fit`, `gender`, `outfit_type`, `style_summary` (all nullable).
- When adding a new field to `OutfitSearch`, make it `blank=True, null=True` so existing rows are not broken.
- Do not delete or rename existing migration files; use `squashmigrations` if the history becomes unwieldy.

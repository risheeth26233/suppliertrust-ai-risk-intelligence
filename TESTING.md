# Testing

## Local checks

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest -q
cd frontend
npm ci
npm run build
```

## Full browser workflow

Run `.\tests\run_browser_local.ps1` from the repository root on Windows. It creates a temporary SQLite database seeded with a synthetic screening fixture, starts isolated API, writable local UI, and read-only demo UI processes, uses installed Edge or Chrome, and stops its own servers afterward. It does not modify the normal `suppliertrust.db` file.

The Playwright workflow covers supplier creation, identifier validation, evidence, synthetic screening and review, performance observations, audit history, report download, editing, search, mobile layout, and checks that public demo controls and uploads are absent. It saves desktop and mobile screenshots to `output/playwright/`.

## PostgreSQL parity

Set `DATABASE_URL` to a disposable PostgreSQL database, run `python -m alembic upgrade head`, then run `python -m pytest -q`. GitHub Actions provisions a fresh PostgreSQL 16 service and runs migrations and the full API integration suite against it, including demo-mode security regressions.

CI installs Chromium, starts isolated API and frontend servers, runs the same browser workflow against local and demo builds, and uploads screenshots plus server logs as the `suppliertrust-browser-results` artifact.

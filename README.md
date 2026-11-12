# SupplierTrust

SupplierTrust is a local-first supplier due-diligence prototype. It records supplier details, reviewer evidence, PDF text extraction, screening results, performance observations, audit events, and explainable risk indicators.

The public-demo configuration is intentionally **read-only** and uses one fixed fictional scenario. It accepts no supplier data or documents, makes no writes, and does not access the application database except for a health check. The full create/edit/review workflow is for local development and automated testing only.

## Run the local application

Requires Python 3.10+ and Node.js 20+. In separate terminals, from the project root:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173. SQLite is the local default (`suppliertrust.db`). `SUPPLIERTRUST_DB` can select another SQLite file. Do not use real supplier records or documents.

## Public demo configuration

The fictional, read-only demo is live at [suppliertrust-ai-risk-intelligence.vercel.app](https://suppliertrust-ai-risk-intelligence.vercel.app). Its API runs on Render and uses an isolated Neon PostgreSQL database; deployment and verification details are in [DEPLOYMENT.md](DEPLOYMENT.md) and [PROJECT_STATUS.md](PROJECT_STATUS.md).

The Vercel frontend is built with `VITE_DEMO_MODE=true` and `VITE_API_URL=https://suppliertrust-api-hp5b.onrender.com`. Render has:

- `SUPPLIERTRUST_MODE=demo`
- `DATABASE_URL` set to the isolated Neon PostgreSQL URL (required by the Render startup check)
- `SUPPLIERTRUST_ALLOWED_ORIGINS` set to the exact deployed Vercel origin, without a wildcard

Demo mode returns fixed fictional data from `/api/demo/*`, allows only `GET` on an explicit route allowlist, applies a process-wide 120 requests/minute cap, disables API docs, and returns security headers. All writes, uploads, reviewer decisions, screening runs, and dataset refreshes are denied. The standard local API is blocked. No visitor records are created, so visitors cannot access one another's data. The demo banner identifies the sample as fictional and read-only.

The hosted service is deliberately small and may sleep or become unavailable after free-tier usage limits are reached. It contains only synthetic demo information; do not enter real supplier information.

## What the risk indicators mean

GSTIN/CIN checks validate format, not registration. A name similarity is not identity confirmation. Delivery/defect inputs are reviewer-entered. Missing evidence and other indicators require human review. The score is a deterministic indicator index, not a trained AI model, fraud probability, or compliance decision. PDF processing extracts text only and does not verify authenticity or OCR images.

Only local development can refresh the official OFAC SDN CSV. The public demo uses a synthetic screening example, not sanctions data. No World Bank or registry APIs are connected.

## Verification

See [TESTING.md](TESTING.md) for the backend, PostgreSQL, frontend, and Playwright workflow. CI uses a disposable PostgreSQL service and captures browser screenshots as workflow artifacts. Known limits and last observed results are in [PROJECT_STATUS.md](PROJECT_STATUS.md).

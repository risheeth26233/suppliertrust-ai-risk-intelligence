# API reference

The backend is FastAPI. Local mode exposes interactive docs at `/docs`; they are disabled in public demo mode.

## Local writable API

Run the backend at `http://127.0.0.1:8000`. Local routes include:

- `GET/POST /api/suppliers`, `GET/PUT/DELETE /api/suppliers/{id}`
- `POST /api/suppliers/{id}/evidence`, `/documents`, and `/performance`
- `GET /api/suppliers/{id}/report`
- `GET /api/screening/status`, `POST /api/screening/ofac/refresh`
- `POST /api/suppliers/{id}/screen`
- `POST /api/screenings/{screen_id}/decision`

PDF extraction accepts PDF files only and has size/page/text limits. Local mode is a single-user prototype and should remain bound to localhost.

## Public read-only API

The public service is `https://suppliertrust-api-hp5b.onrender.com`. It serves only fictional demo data:

- `GET /healthz` checks database connectivity with `SELECT 1`.
- `GET /api/demo/suppliers` lists the fixed fictional sample.
- `GET /api/demo/suppliers/{id}` returns the sample profile (`id` 1 only).
- `GET /api/demo/suppliers/{id}/report` returns its fictional text report.
- `GET /api/demo/screening/status` describes the synthetic fixture.

Other routes and write methods return 403 in demo mode. The API allows CORS only from the configured production Vercel origin. Browser preflight is limited to GET on the demo read routes; no write preflight is permitted.

## Interpretation

Identifier checks validate format only. Public screening is synthetic and is not an official-list lookup. Local OFAC screening compares names from the cached SDN dataset; potential matches require human review. The risk index is deterministic and is not a probability of fraud or a regulatory decision.

# Public demo deployment

The fictional, read-only public demo is deployed at https://suppliertrust-ai-risk-intelligence.vercel.app. Backend: https://suppliertrust-api-hp5b.onrender.com. It uses a dedicated Render Hobby workspace/service and isolated Neon Free PostgreSQL project; no card was added.

## Backend: Render + Neon

The root `render.yaml` defines one Free Render web service. It does not create a database and leaves `DATABASE_URL` and allowed origins as manual values. The service uses an isolated Neon PostgreSQL database. Render start-up fails closed if the service is on Render without `SUPPLIERTRUST_MODE=demo`, `DATABASE_URL`, or an explicit origin list.

Render runs Alembic migrations during build and starts Uvicorn on `0.0.0.0:$PORT`. `/healthz` checks database connectivity. Render must be configured with:

```text
SUPPLIERTRUST_MODE=demo
DATABASE_URL=<Neon pooled PostgreSQL URL with TLS>
SUPPLIERTRUST_ALLOWED_ORIGINS=https://suppliertrust-ai-risk-intelligence.vercel.app
```

Keep the URL in Render's secret environment settings; never add it to GitHub, Vercel, or source files. Demo mode serves static fictional data only, rejects every non-GET request and every non-demo API route, disables docs, and limits API requests. No visitor supplier data or documents are accepted or persisted.

## Frontend: Vercel

The Vercel project root is `frontend`. `frontend/vercel.json` defines browser security headers and a content security policy. Build-time variables:

```text
VITE_DEMO_MODE=true
VITE_API_URL=https://suppliertrust-api-hp5b.onrender.com
```

`SUPPLIERTRUST_ALLOWED_ORIGINS` is the exact Vercel production origin. No preview origins or wildcard origins are allowed. The CSP allows API requests only to the deployed Render service.

## Hosted smoke check

Hosted checks:

1. `GET https://suppliertrust-api-hp5b.onrender.com/healthz` returns `{"status":"ok"}`; the handler runs `SELECT 1` against Neon.
2. `GET /api/demo/suppliers` returns the one fixed fictional record; profile and report routes return fictional evidence, synthetic screening, and report content.
3. `POST /api/suppliers`, `POST /api/demo/suppliers`, `POST /api/screening/ofac/refresh`, document upload, decisions, and legacy `/api/suppliers` reads return `403`.
4. CORS preflight succeeds for GET on allowlisted demo routes from the exact Vercel production origin. Write preflights and origins outside the allowlist are rejected.
5. The frontend shows the read-only fictional-demo banner, and response headers include CSP, HSTS, no-store, nosniff, frame denial, and restricted permissions.
6. Browser verification of supplier loading, report download, mobile layout, and console errors is being repeated after the CORS preflight fix is deployed.

Local development remains writable and uses SQLite by default. Do not connect the public site to the local-development API mode. Enabling public writes requires authentication, tenant isolation, ownership-scoped queries, upload isolation, and a separate security review; those are not part of this read-only demo.

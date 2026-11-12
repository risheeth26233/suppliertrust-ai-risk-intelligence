# Deployment preparation (not deployed)

The checked-in configuration prepares a fictional, read-only demo. No Vercel, Render, or Neon resource has been created. Do not deploy until the exact environment variables and service origins are supplied and reviewed.

## Backend: Render + Neon

The root `render.yaml` defines one Free Render web service. It does not create a database and leaves `DATABASE_URL` and allowed origins as manual values. Configure an isolated Neon PostgreSQL database and set its pooled PostgreSQL connection string as `DATABASE_URL`. Render start-up fails closed if the service is on Render without `SUPPLIERTRUST_MODE=demo`, `DATABASE_URL`, or an explicit origin list.

Render runs Alembic migrations during build and starts Uvicorn on `0.0.0.0:$PORT`. `/healthz` checks database connectivity. Render must be configured with:

```text
SUPPLIERTRUST_MODE=demo
DATABASE_URL=<Neon pooled PostgreSQL URL with TLS>
SUPPLIERTRUST_ALLOWED_ORIGINS=https://<exact-vercel-project>.vercel.app
```

Keep the URL in Render's secret environment settings; never add it to GitHub, Vercel, or source files. Demo mode serves static fictional data only, rejects every non-GET request and every non-demo API route, disables docs, and limits API requests. No visitor supplier data or documents are accepted or persisted.

## Frontend: Vercel

Set the Vercel project root to `frontend`. `frontend/vercel.json` defines browser security headers and a content security policy. Set build-time variables:

```text
VITE_DEMO_MODE=true
VITE_API_URL=https://<render-service>.onrender.com
```

Set `SUPPLIERTRUST_ALLOWED_ORIGINS` on Render to the exact Vercel production URL (and add any desired preview origin explicitly). Do not use wildcard origins. The CSP allows API requests only to the named `suppliertrust-api.onrender.com` Render service; if the Render service hostname differs, update the CSP before building.

## Hosted smoke check

After a separately authorized deployment:

1. Confirm `GET https://<render-service>.onrender.com/healthz` returns `{"status":"ok"}`.
2. Confirm `GET /api/demo/suppliers` returns only the fixed fictional record.
3. Confirm `POST /api/suppliers`, `POST /api/demo/suppliers`, `POST /api/screening/ofac/refresh`, all upload paths, and legacy `/api/suppliers` reads return `403`.
4. Confirm the Vercel page shows the read-only fictional-demo banner, loads the sample profile/report, and contains no enabled write or upload controls.
5. Confirm an unlisted Origin cannot read the API response via browser CORS; no `Access-Control-Allow-Origin` should be returned for it.
6. Review Render logs for secrets or supplier data; public demo should not receive either.

Local development remains writable and uses SQLite by default. Do not connect the public site to the local-development API mode. Enabling public writes requires authentication, tenant isolation, ownership-scoped queries, upload isolation, and a separate security review; those are not part of this read-only demo.

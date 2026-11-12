# Project status

## Implemented

SupplierTrust is a local-first supplier due-diligence prototype with supplier records, identifier format checks, reviewer-entered evidence, PDF text extraction, screening and human decisions, sourced performance observations, explainable risk indicators, audit events, and text reports. The React workspace includes overview, directory, profile, evidence, performance, audit, and screening workflows with responsive layouts and restrained motion.

The public showcase is read-only and serves a fixed fictional scenario. It denies writes, uploads, local-data routes, screening refreshes, and decisions; applies an explicit route allowlist, request cap, response security headers, and exact-origin CORS. It does not read supplier records from the database. The public frontend is [suppliertrust-ai-risk-intelligence.vercel.app](https://suppliertrust-ai-risk-intelligence.vercel.app); the API is [suppliertrust-api-hp5b.onrender.com](https://suppliertrust-api-hp5b.onrender.com).

## Verification status (2026-11-12)

- API integration suite: **6 passed** locally against SQLite.
- Alembic SQLite migration through head (including snapshot provenance) and repeat upgrade: passed.
- Vite production build: passed.
- Playwright desktop and mobile workflow in installed Microsoft Edge: passed. It exercised supplier creation/edit/search/deletion, evidence, synthetic screening and review, performance observation, activity, report download, read-only demo controls, JavaScript errors, and mobile overflow. Screenshots are captured under the ignored `output/playwright/` directory.
- Render Blueprint and Vercel JSON parse successfully; provider-specific configuration was cross-checked against current provider documentation.
- PostgreSQL integration is configured in GitHub Actions using an ephemeral PostgreSQL service. The workflow passed for commit `b7ad81c` (API tests, migrations, frontend build, and Chromium browser workflow); local verification also passed against SQLite.
- No hosted deployment or hosted smoke test was performed.

## Hosted deployment (2026-11-13)

- Vercel frontend deployed on the Hobby tier with `VITE_DEMO_MODE=true` and the dedicated Render API URL.
- Dedicated Render Hobby workspace; backend service is Free and uses the isolated Neon Free project. No payment method was added.
- Render `/healthz` returned `{"status":"ok"}` after the PostgreSQL migration. The endpoint performs `SELECT 1`, confirming a working TLS PostgreSQL connection.
- API checks returned the fictional supplier, evidence, synthetic screening fixture, and downloadable fictional report. Legacy/local supplier routes, writes, uploads, decisions, and live screening refresh returned 403. Exact-origin CORS and response security headers were checked.
- Initial browser verification found that demo middleware blocked CORS preflight. A minimal backend fix now permits only GET preflights on the explicit demo read-route allowlist; all other preflights and write operations remain denied. This fix is pending push and Render auto-deploy, then the browser check must be repeated before considering hosted verification complete.
- Vite production build passed after this change. The complete API pytest run did not finish in the local runner and was stopped; the preceding verified commit `fbb604f` has passing PostgreSQL, API, build, and Playwright CI.

## Known limits

- No authentication, authorization, or per-user data isolation for the writable local application. Keep it bound to localhost; do not use real supplier records or documents.
- GSTIN/CIN checks validate format only. Evidence and operational observations are reviewer-supplied.
- PDF processing extracts text only; it does not authenticate documents or OCR images.
- OFAC SDN is the only live screening source in local mode. No World Bank or company registry APIs are connected. Similarity matching requires human review and does not establish identity.
- No trained AI model is used. The score is a deterministic indicator index, not a fraud probability or compliance decision.
- The free-tier services may sleep or suspend at their included usage limits. The application has no user authentication because the public dataset is static and fictional; no real supplier records or documents should be submitted.

# Project status

## Implemented

SupplierTrust is a local-first supplier due-diligence prototype with supplier records, identifier format checks, reviewer-entered evidence, PDF text extraction, screening and human decisions, sourced performance observations, explainable risk indicators, audit events, and text reports. The React workspace includes overview, directory, profile, evidence, performance, audit, and screening workflows with responsive layouts and restrained motion.

The prepared public showcase is read-only and serves a fixed fictional scenario. It denies writes, uploads, local-data routes, screening refreshes, and decisions; applies an explicit route allowlist, request cap, response security headers, and exact-origin CORS. It does not read supplier records from the database. Render and Vercel configuration is included, but no service has been deployed.

## Verification status (2026-11-12)

- API integration suite: **6 passed** locally against SQLite.
- Alembic SQLite migration through head (including snapshot provenance) and repeat upgrade: passed.
- Vite production build: passed.
- Playwright desktop and mobile workflow in installed Microsoft Edge: passed. It exercised supplier creation/edit/search/deletion, evidence, synthetic screening and review, performance observation, activity, report download, read-only demo controls, JavaScript errors, and mobile overflow. Screenshots are captured under the ignored `output/playwright/` directory.
- Render Blueprint and Vercel JSON parse successfully; provider-specific configuration was cross-checked against current provider documentation.
- PostgreSQL integration is configured in GitHub Actions using an ephemeral PostgreSQL service. Local verification used SQLite; the PostgreSQL-backed Actions result is pending for the current push.
- No hosted deployment or hosted smoke test was performed.

## Known limits

- No authentication, authorization, or per-user data isolation for the writable local application. Keep it bound to localhost; do not use real supplier records or documents.
- GSTIN/CIN checks validate format only. Evidence and operational observations are reviewer-supplied.
- PDF processing extracts text only; it does not authenticate documents or OCR images.
- OFAC SDN is the only live screening source in local mode. No World Bank or company registry APIs are connected. Similarity matching requires human review and does not establish identity.
- No trained AI model is used. The score is a deterministic indicator index, not a fraud probability or compliance decision.
- Public demo infrastructure is prepared but not deployed. A real isolated PostgreSQL database, exact Vercel origin, service secrets, and a separate deployment authorization are still required.

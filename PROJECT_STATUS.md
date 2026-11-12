# Project status

## Implemented

SupplierTrust now has a local-first backend and React workspace for supplier records, identifier format checks, reviewer-entered evidence, PDF text extraction and discrepancy hints, user-triggered OFAC SDN refresh and screening, human screening decisions, sourced delivery/defect observations, explainable risk factors, audit events, and text reports. The frontend includes overview, directory, supplier profile, evidence, performance, audit, and screening workflows with responsive layouts and motion styling.

SQLite is the local default. SQLAlchemy supports PostgreSQL URLs and Alembic defines the schema and performance/audit migrations. GitHub Actions runs Alembic migrations, the API integration suite, and the frontend production build.

## Verification status (2026-11-12)

- API suite: 5 passed locally against SQLite.
- Fresh SQLite Alembic migration was applied through head and reapplied successfully.
- Vite production build passed after the frontend performance, source-status, and audit UI changes.
- Latest observed GitHub Actions run passed the database migration, API tests, and production build for commit `cf71969`.
- Local browser visual smoke check could not connect to loopback services in this restricted environment; no claim of full UI end-to-end verification is made.

## Limitations

- No authentication, authorization, or per-user data isolation. Keep the API bound to localhost; do not deploy publicly or use real supplier records.
- GSTIN and CIN checks validate format only. Evidence and operational observations are supplied by the reviewer.
- PDF processing extracts text only; it does not authenticate documents or OCR images.
- OFAC SDN is the only live source. No World Bank or company registry APIs are connected. Similarity matching requires reviewer adjudication and does not establish identity.
- No trained AI model is used. The score is an indicator index, not a fraud probability or compliance decision.
- PostgreSQL migration syntax and the adapter have been validated with SQLite migration checks, but have not been exercised against a live PostgreSQL server.
- The frontend build is verified; full browser interaction and accessibility testing remain outstanding.

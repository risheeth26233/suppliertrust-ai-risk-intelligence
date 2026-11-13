# Project status

## UI/UX transformation (2026-11-13)

- Replaced the former three-view screen with a responsive enterprise intelligence workspace using the existing React/Vite/Lucide stack; no dependencies were added.
- Added grouped navigation with pointer/keyboard previews and mobile tap help, dismissible page introductions with persistent help, and an eight-step tour that navigates to and highlights real pages.
- Added data-backed command-center metrics, a real risk distribution, purpose-built featured supplier view, and supplier-specific risk, evidence, screening, performance, activity, and text-report pages. Each view states data limits; no synthetic trend or AI prediction was added.
- Preserved local supplier CRUD, evidence entry, PDF text extraction, screening, human decisions, performance entry, audit history, and text reports. Public demo remains read-only and hides writes, uploads, decisions, and live screening actions.
- Added a Vercel SPA rewrite for deep links. Security headers and the allowed Render API origin are unchanged.
- Local verification: `python -m pytest -q` passed (6 tests); `npm run build` passed; updated Playwright workflow passed on Microsoft Edge, including local write workflows, report download, guided tour, Back/Forward, touch navigation, mobile overflow checks at 390px/375px, and public-demo control restrictions. Captured screenshots are in the ignored local `output/playwright/` directory.
- GitHub Actions passed for commit [`b3d3f75`](https://github.com/risheeth26233/suppliertrust-ai-risk-intelligence/commit/b3d3f75f6f660ee9f82dbea576b5c8b0b8ffac9c) in [run 15](https://github.com/risheeth26233/suppliertrust-ai-risk-intelligence/actions/runs/43450357728).
- The existing Vercel project deployed successfully as `dpl_6EXZL5AAR2z9bTjAbLNQwYZ4viNu`; the production alias is [suppliertrust-ai-risk-intelligence.vercel.app](https://suppliertrust-ai-risk-intelligence.vercel.app). No Vercel project or paid service was created.
- Hosted Playwright checks passed against the actual site: dashboard and supplier profile data loaded, risk/evidence/screening/performance/activity/report routes worked, the text report downloaded, `/suppliers/1/risk` loaded directly, and the 375px mobile layout had no horizontal overflow. Browser exceptions and console errors: zero.
- The live Render `/healthz` returned 200, and the demo API returned the one fictional supplier. Five public write/protected routes (supplier POST, legacy supplier GET, OFAC refresh, document upload, and screening decision) returned 403. Public interface controls for writes and uploads were absent. Render and its isolated Neon database were unchanged by this redesign.
- Live screenshots are saved in the ignored local `output/playwright/` directory.

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
- At the time of this local/CI verification record, hosted deployment had not yet been performed; hosted results are recorded below.

## Hosted deployment (2026-11-13)

- Vercel frontend deployed on the Hobby tier with `VITE_DEMO_MODE=true` and the dedicated Render API URL.
- Dedicated Render Hobby workspace; backend service is Free and uses the isolated Neon Free project. No payment method was added.
- Render `/healthz` returned `{"status":"ok"}` after the PostgreSQL migration. The endpoint performs `SELECT 1`, confirming a working TLS PostgreSQL connection.
- API checks returned the fictional supplier, evidence, synthetic screening fixture, and downloadable fictional report. Legacy/local supplier routes, writes, uploads, decisions, and live screening refresh returned 403. Exact-origin CORS and response security headers were checked; GET preflight returned 200 while POST preflight returned 403.
- The first browser check exposed blocked CORS preflight; a later sweep also found a missing favicon. GET-only preflight handling was deployed to Render, and the branded favicon plus demo-specific UI copy was deployed to Vercel.
- The hosted browser check passed after those fixes: public page and API loaded, the fictional profile/risk/evidence/synthetic screening appeared, report download worked, and the favicon returned 200. Desktop (1440×1000) and mobile (390×844) had no horizontal overflow, with no write controls, failed requests, or console errors.
- Neon connectivity was verified through `/healthz` (`SELECT 1`), and the isolated Neon project is on its Free plan with its migrated SupplierTrust schema. The public frontend bundle contains no database URL or credential material.
- GitHub Actions passed for commit `2cae651` with PostgreSQL migrations, API tests, Vite build, and desktop/mobile Playwright. The final favicon/copy correction is covered by the same workflow; confirm its commit-specific result in the linked Actions run.

## Known limits

- No authentication, authorization, or per-user data isolation for the writable local application. Keep it bound to localhost; do not use real supplier records or documents.
- GSTIN/CIN checks validate format only. Evidence and operational observations are reviewer-supplied.
- PDF processing extracts text only; it does not authenticate documents or OCR images.
- OFAC SDN is the only live screening source in local mode. No World Bank or company registry APIs are connected. Similarity matching requires human review and does not establish identity.
- No trained AI model is used. The score is a deterministic indicator index, not a fraud probability or compliance decision.
- The free-tier services may sleep or suspend at their included usage limits. The application has no user authentication because the public dataset is static and fictional; no real supplier records or documents should be submitted.

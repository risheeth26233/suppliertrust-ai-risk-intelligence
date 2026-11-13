# Architecture

SupplierTrust has a React/Vite frontend and a FastAPI backend. The frontend calls the backend with JSON over HTTP; Vite serves the local development UI on `127.0.0.1:5173` and the API on `127.0.0.1:8000`.

## Local workspace

Local mode is writable. SQLite is the default database, and Alembic manages schema migrations. Supplier records, evidence, performance observations, synthetic or cached screening results, and audit events are stored locally. Risk indicators are deterministic and calculated from those records; they are not a trained AI model or a probability of fraud. PDF text extraction runs in-process and stores uploaded files in a private local directory.

## Public demo

The public Vercel frontend uses `VITE_DEMO_MODE=true` and calls the dedicated Render API. Render runs FastAPI in demo mode and connects to the isolated Neon PostgreSQL database for `/healthz` only. Demo data comes from one fixed fictional fixture, not supplier rows in PostgreSQL. Only explicitly allowlisted GET routes are served; GET CORS preflights are limited to those routes and the exact configured origin. Writes, uploads, decisions, screening refreshes, and local supplier routes are blocked.

The public and local modes share the codebase, but the public mode has no workflow for creating, editing, or uploading records. See [DEPLOYMENT.md](DEPLOYMENT.md) for hosted resource details and [SECURITY.md](SECURITY.md) for boundaries.

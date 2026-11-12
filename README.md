# SupplierTrust

SupplierTrust is an early local-first supplier due-diligence workspace. It helps reviewers record supplier-provided information and evidence, test a fictional entity-matching workflow, and see transparent risk indicators. It is **not a complete MVP or production-ready service**.

## Start locally

Requires Python 3.10+ and Node.js 20+. In two terminals from the project directory:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. SQLite data is stored in `suppliertrust.db`; set `SUPPLIERTRUST_DB` to change its location. Use fictional records only. The API is deliberately bound to localhost: no authentication or user isolation is implemented.

## Demo workflow

Add a fictional supplier, enter an identifier, open its profile and record a source URL, date, notes and reviewer. Run **synthetic fixture** screening; the fictional name `Fictional Example Trading Co` produces a candidate. Review it as a false positive or confirmed fixture and download a text report. The directory supports editing and searching. No live sanctions check is performed.

## Method and limitations

GSTIN checksum and CIN syntax checks do not confirm registration. Manual evidence status reflects the reviewer’s assertion, not an automated official check. Name normalization and sequence similarity use Python's standard library, not an LLM or trained model. Screening compares only one invented fixture; similarity is not identity verification. Live OFAC, World Bank, and registry APIs are not connected. Document upload, OCR, PostgreSQL/Alembic, authentication, audit history, PDF reports, and production deployment are not implemented.

The score adds 20 when no manually verified evidence is recorded, 15 for an unrecognized/invalid identifier, and 30 for a pending or reviewer-confirmed fixture match. A false-positive decision removes the match contribution. It is an indicator index, **not a fraud probability**, and does not imply wrongdoing. Coverage is the fraction of three activities present: identifier supplied, any evidence recorded, and fixture screening run. It measures workflow completion, not evidence quality. Confidence is a simple coverage label, not a statistical measure. Scores and evidence are recalculated from current records; assessment history is not stored.

## Verification

`python -m pytest` runs the API suite. `npm run build` builds the frontend. CI is configured in `.github/workflows/ci.yml`, but has not yet been observed on GitHub. See `PROJECT_STATUS.md` for actual local test results and outstanding work.

OFAC screening: use the user-triggered refresh button to download the official SDN CSV. Refresh sends a User-Agent, validates the redirected host and dataset size, parses the headerless legacy CSV, stores the retrieval timestamp and digest, and retains the prior snapshot if refresh fails. Screening refuses data older than seven days, ranks likely name candidates, and leaves decisions for a reviewer. This covers OFAC SDN only; it is not a comprehensive sanctions-screening service.

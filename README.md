# SupplierTrust

SupplierTrust is a local-first supplier due-diligence workspace for recording supplier details, source-backed evidence, PDF text extraction, delivery observations, screening results, and reviewer activity. Its dashboard summarizes recorded indicators and explains the source of each factor.

This is a prototype for fictional data and local evaluation. It is not a production compliance or fraud-detection service. The risk score is an explainable concern index, not a probability or finding of wrongdoing.

## Run locally

Requires Python 3.10+ and Node.js 20+. From the project root, start the API:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. The UI uses `http://127.0.0.1:8000` by default. Set `VITE_API_URL` to the API origin when it runs elsewhere. SQLite data is stored in `suppliertrust.db`; `SUPPLIERTRUST_DB` changes the path. Use fictional records only.

## Features

- Supplier create, edit, search, sort, profile, and delete workflows.
- GSTIN checksum and CIN format checks; these do not verify registration or company status.
- Reviewer-entered evidence with source URL, date, reviewer, and notes.
- PDF-only intake up to 5 MB, text extraction, and basic name/identifier discrepancy hints. This does not authenticate a document and does not OCR images.
- User-triggered refresh of the official OFAC SDN CSV, with retrieval date, SHA-256 digest, and a seven-day freshness limit. Potential name matches require a human decision; a name match is not identity confirmation and the SDN list is not complete sanctions coverage.
- Reviewer-entered delivery and defect observations with source URLs. These can contribute explainable risk factors.
- Supplier review audit events, a downloadable text report, and an overview dashboard.
- SQLite locally; PostgreSQL connections through SQLAlchemy and Alembic migrations.

## Data and limitations

The score adds documented indicators from the data currently recorded (including missing manually verified evidence, identifier format issues, pending screening matches, and recorded performance concerns). Coverage measures completion of selected workflow fields, not evidence quality. Confidence is a simple label, not a statistical confidence estimate.

The app does not connect to World Bank or company registry APIs, does not use a trained AI model, does not provide image OCR, and has no authentication or user isolation. PostgreSQL is supported by the code and migrations, but has not been integration-tested against a live PostgreSQL server. Keep the API bound to localhost and do not use real supplier data or deploy publicly without security, privacy, and compliance review.

## Verification

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest -q
cd frontend
npm run build
```

GitHub Actions runs the database migration, API suite, and frontend production build. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the current verification and remaining limitations.

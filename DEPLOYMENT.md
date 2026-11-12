# Deployment

The app supports SQLite for local development and PostgreSQL through `DATABASE_URL` (SQLAlchemy + psycopg). PostgreSQL schema changes are managed with Alembic:

```powershell
python -m pip install -r requirements.txt
$env:DATABASE_URL = "postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require"
python -m alembic upgrade head
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Use a dedicated database; do not share databases with InvoiceIQ or Healthcare-App. No cloud database or paid resources have been created.

Public multi-user deployment is not ready: login, authorization, tenant isolation, and analyst audit history are not implemented. Keep the API on localhost and use fictional supplier records until those controls are built and reviewed. Uploaded PDFs use a private local directory; configure `SUPPLIERTRUST_UPLOAD_DIR` to a persistent private volume for deployments.

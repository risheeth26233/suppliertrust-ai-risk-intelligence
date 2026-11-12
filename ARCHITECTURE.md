# Architecture

React/Vite talks to a local FastAPI service using JSON. The service stores supplier, evidence and synthetic screening records in SQLite with foreign keys. Risk indicators are calculated on read. The database uses parameterized queries. This is a local prototype; no multi-user isolation, real source ingestion, file storage or migration system exists.

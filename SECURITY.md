# Security

Local-only prototype: there is no authentication, authorization, audit trail or per-user isolation. Do not expose it to a network or enter sensitive supplier data. It does not fetch arbitrary evidence URLs and does not accept uploads. Input uses Pydantic validation and SQL queries are parameterized. Source links are user-supplied assertions and should be checked independently. Never commit credentials, private data or the SQLite database.

PDF files are checked by extension, declared MIME type, signature and size, then parsed in-process for up to 20 pages / 100,000 characters. Store directory is local and private; there is no document download route. This limits exposure but is not a hardened malware sandbox. Use trusted fictional PDFs only in this prototype.

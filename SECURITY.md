# Security

Local-only prototype: there is no authentication, authorization, audit trail or per-user isolation. Do not expose it to a network or enter sensitive supplier data. It does not fetch arbitrary evidence URLs and does not accept uploads. Input uses Pydantic validation and SQL queries are parameterized. Source links are user-supplied assertions and should be checked independently. Never commit credentials, private data or the SQLite database.

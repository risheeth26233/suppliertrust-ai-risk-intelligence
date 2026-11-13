# Security and data boundaries

## Public demo

The deployed demo displays one fixed fictional supplier and synthetic evidence/screening data. It does not read supplier records from Neon. In demo mode, the backend serves only an explicit GET route allowlist and a health check. It rejects writes, uploads, screening refreshes, reviewer decisions, and the regular supplier API. GET preflights are accepted only for allowlisted routes, from the exact Vercel origin, with the allowed `Content-Type` header. The API applies a request cap and returns security headers; the Vercel frontend CSP permits only its configured Render API host.

The demo has no login because its data is public and fictional. Do not submit real supplier information, documents, or credentials.

## Local application

Local mode is a writable prototype and has no authentication, authorization, or per-user data isolation. Bind the API to localhost and use fictional records only. Never expose local mode to a public network or commit credentials, private data, or the SQLite database.

PDF uploads are limited by extension, declared MIME type, signature, size, page count, and extracted text length. Parsing happens in-process and is not a hardened malware sandbox. Store files in the private local upload directory; there is no document download route. Treat documents as untrusted input.

## Interpretation limits

GSTIN/CIN checks validate format only. Evidence and delivery observations are reviewer-entered. PDF text extraction does not verify authenticity or OCR images. The synthetic public screening fixture is not sanctions data. Local OFAC name matches are candidates for human review and do not establish identity or wrongdoing. Risk scores are deterministic indicator indexes, not trained-AI results, fraud probabilities, or compliance decisions.

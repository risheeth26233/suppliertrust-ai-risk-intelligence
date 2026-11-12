# Project status

Early implementation, not acceptance complete. SQLite-backed supplier CRUD, manually recorded evidence, identifier format checks, synthetic matching, reviewer decisions, a risk indicator calculation, a React UI and text reports are implemented. No real external sources are retrieved. The React build and full end-to-end browser workflow require installed frontend packages. PostgreSQL, migrations, real sanctions data, document processing, authentication and assessment history remain outstanding. Do not deploy publicly or use real supplier data.

Verification on 2026-11-12: two API integration tests passed outside the sandbox; the Vite production build passed. A browser smoke test created a fictional supplier, recorded unverified evidence, and ran the synthetic fixture. The browser test did not cover review decisions, reports, editing, responsive breakpoints, or accessibility in full; the API test covers decisions and reports. GitHub CI and full acceptance remain unverified.

PDF document intake is now supported locally with a 5 MB limit, MIME and signature checks, bounded text extraction, local private storage, and basic name/identifier comparison. It does not authenticate documents or provide image OCR. These capabilities are a prototype and require security review before use beyond localhost.

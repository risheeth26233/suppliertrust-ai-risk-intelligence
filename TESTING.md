# Testing

Run `python -m pytest` and `npm run build`. The API tests exercise CRUD, search, identifier checks, evidence, fixture screening, false-positive review and report generation. Browser end-to-end tests, real source failure tests, and document tests are not yet implemented. Consult PROJECT_STATUS.md for current execution status.

Local results on 2026-11-12: 2 API tests passed and the Vite production build passed. Browser smoke test covered supplier creation, format validation, evidence entry, and fixture screening. Full browser acceptance remains outstanding.

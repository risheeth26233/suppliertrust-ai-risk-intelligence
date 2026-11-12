# API

All endpoints are local-only and available in FastAPI's interactive docs at `/docs` when the API runs. Supplier CRUD uses `GET/POST /api/suppliers`, `GET/PUT/DELETE /api/suppliers/{id}`. Evidence, PDF and performance inputs use `POST /api/suppliers/{id}/evidence`, `/documents`, and `/performance`. OFAC dataset freshness and refresh use `GET /api/screening/status` and `POST /api/screening/ofac/refresh`; supplier screening is `POST /api/suppliers/{id}/screen`, with human decisions at `POST /api/screenings/{screen_id}/decision`. Download the text assessment at `GET /api/suppliers/{id}/report`.

The identifier check validates format only. OFAC screening compares names against the locally cached official SDN CSV; results are possible matches and require analyst review. Performance metrics are reviewer-entered and their evidence sources are shown. No registry API or World Bank debarment source is currently integrated.

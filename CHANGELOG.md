# Changelog

## 0.2.0 - Deployment hardening

- Added environment-driven runtime configuration (`HOST`, `PORT`, `LITTUP_API_*`, `LITTUP_DATA_DIR`, `LITTUP_DB_PATH`, `LITTUP_ENV`, `LITTUP_LOG_LEVEL`).
- Replaced in-Streamlit API spawning with a production-safe dual-process startup script (`start.sh`).
- Added Docker deployment support (`Dockerfile`, `.dockerignore`, healthcheck).
- Added `.env.example` and Streamlit production config.
- Added persistence-safe directory initialization for database and project storage.
- Expanded smoke tests for import, DB init, project/template flow, and API health.
- Added GitHub Actions CI for pytest + Docker build validation.
- Added deployment documentation (`DEPLOYMENT.md`) and updated README deployment guidance.

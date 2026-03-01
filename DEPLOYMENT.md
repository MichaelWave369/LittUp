# LittUp Deployment Guide

## 1. Deployment architecture

LittUp runs as a single container with two Python processes:

1. **FastAPI companion API** (internal only) on `LITTUP_API_HOST:LITTUP_API_PORT`.
2. **Streamlit UI** (public) on `HOST:PORT`.

`start.sh` starts FastAPI once, then Streamlit in the foreground.

## 2. Required runtime assumptions

- Python 3.10+
- Writable persistent storage for:
  - SQLite database (`LITTUP_DB_PATH`)
  - Project folders (`LITTUP_PROJECTS_DIR`)

## 3. Docker runbook

```bash
docker build -t littup:latest .
docker run --rm -p 8501:8501 \
  -e LITTUP_ENV=production \
  -e HOST=0.0.0.0 \
  -e PORT=8501 \
  -e LITTUP_API_HOST=127.0.0.1 \
  -e LITTUP_API_PORT=8756 \
  -v $(pwd)/.littup-data:/data/littup \
  littup:latest
```

## 4. Health checks

- Container-level (public app): `http://127.0.0.1:${PORT}/_stcore/health` (path is `/_stcore/health`)
- Internal API: `http://127.0.0.1:8756/health`

## 5. Railway deploy

1. Push repo to GitHub.
2. Create Railway project from repo.
3. Railway will use `Dockerfile` + `railway.json`.
4. Add persistent volume mounted at `/data/littup`.
5. Set **Healthcheck Path** to `/_stcore/health`.

## 6. Troubleshooting

### API companion unavailable in sidebar
- Confirm `start.sh` is used.
- Verify `LITTUP_API_HOST` and `LITTUP_API_PORT` match both Uvicorn and Streamlit environment.

### DB errors on first boot
- Ensure mount path is writable.
- Confirm `LITTUP_DB_PATH` parent directory exists or allow `start.sh` to create it.

### Data not persisting across restarts
- Confirm platform volume mount points to `/data/littup` or your custom `LITTUP_DATA_DIR`.

### Port bind failures
- Ensure platform injects `PORT`, and expose/map the same port publicly.

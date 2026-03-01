# LittUp v0.2 — The Local AI Code Forge

> Build, debug, and ship software locally with a coordinated multi-agent team.

![LittUp Hero Placeholder](docs/screenshots/hero-placeholder.svg)

LittUp is an all-in-one open-source studio in the Triad369 ecosystem. It is local-first, offline-capable, and private by default. The app combines:

- **Streamlit** for the primary noir interface
- **FastAPI** as an internal companion API
- **SQLite** for project memory, snapshots, and chat logs
- **Local execution sandbox** for run/test loops

## Core Features

- Project dashboard with local template creation
- Multi-agent forge room (Planner, Coder, Tester, Reviewer, Documenter)
- Snapshot history + evolve loop
- Triad369 integrations (Agentora, Memoria, Launchpad)
- Private-by-default local persistence

## Quick Start (Local Development)

```bash
git clone https://github.com/MichaelWave369/LittUp
cd LittUp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# terminal 1: API companion
uvicorn littup.api:app --host 127.0.0.1 --port 8756

# terminal 2: Streamlit UI
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

## Production-like Local Run (single command)

```bash
./start.sh
```

This starts both processes safely:
- FastAPI companion: `LITTUP_API_HOST:LITTUP_API_PORT` (defaults `127.0.0.1:8756`)
- Streamlit public app: `HOST:PORT` (defaults `0.0.0.0:8501` in production mode)

## Docker Deployment

```bash
docker build -t littup:latest .
docker run --rm -p 8501:8501 \
  -e PORT=8501 \
  -e HOST=0.0.0.0 \
  -e LITTUP_ENV=production \
  -v $(pwd)/.littup-data:/data/littup \
  littup:latest
```

Health check endpoints:
- Public app health: `GET /_stcore/health`
- Internal API health: `GET http://127.0.0.1:8756/health` (inside container)

## Configuration

Copy `.env.example` and adjust values:

| Variable | Default | Purpose |
|---|---|---|
| `LITTUP_ENV` | `development` | Runtime mode (`development`/`production`) |
| `LITTUP_LOG_LEVEL` | `info` | API logging level |
| `HOST` | `127.0.0.1` dev / `0.0.0.0` prod | Streamlit bind host |
| `PORT` | `8501` | Streamlit public port |
| `LITTUP_API_HOST` | `127.0.0.1` | Internal FastAPI bind host |
| `LITTUP_API_PORT` | `8756` | Internal FastAPI bind port |
| `LITTUP_DATA_DIR` | `~/.littup` | Root local data directory |
| `LITTUP_DB_PATH` | `$LITTUP_DATA_DIR/littup.db` | SQLite DB path |
| `LITTUP_PROJECTS_DIR` | `$LITTUP_DATA_DIR/projects` | Generated project files |

## Platform Deploy Notes

- **Railway**: Included `railway.json` uses Dockerfile deploy path.
- **Render/Fly/VPS**: Use Dockerfile directly and mount `/data/littup` as a persistent volume.

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for complete deployment and troubleshooting guidance.

## Testing

```bash
pip install pytest
pytest -q
```

## Screenshots

![Dashboard Placeholder](docs/screenshots/dashboard-placeholder.svg)
![Forge Room Placeholder](docs/screenshots/forge-room-placeholder.svg)

## License

MIT

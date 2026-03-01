#!/usr/bin/env bash
set -euo pipefail

export LITTUP_ENV="${LITTUP_ENV:-production}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8501}"
export LITTUP_API_HOST="${LITTUP_API_HOST:-127.0.0.1}"
export LITTUP_API_PORT="${LITTUP_API_PORT:-8756}"

if [[ -n "${LITTUP_DATA_DIR:-}" ]]; then
  mkdir -p "${LITTUP_DATA_DIR}"
fi
if [[ -n "${LITTUP_PROJECTS_DIR:-}" ]]; then
  mkdir -p "${LITTUP_PROJECTS_DIR}"
fi
if [[ -n "${LITTUP_DB_PATH:-}" ]]; then
  mkdir -p "$(dirname "${LITTUP_DB_PATH}")"
fi

uvicorn littup.api:app \
  --host "${LITTUP_API_HOST}" \
  --port "${LITTUP_API_PORT}" \
  --log-level "${LITTUP_LOG_LEVEL:-info}" &
API_PID=$!

cleanup() {
  kill "${API_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

streamlit run app.py \
  --server.headless true \
  --server.address "${HOST}" \
  --server.port "${PORT}" \
  --browser.gatherUsageStats false

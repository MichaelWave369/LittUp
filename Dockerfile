FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

ENV LITTUP_ENV=production \
    HOST=0.0.0.0 \
    PORT=8501 \
    LITTUP_API_HOST=127.0.0.1 \
    LITTUP_API_PORT=8756 \
    LITTUP_DATA_DIR=/data/littup \
    LITTUP_DB_PATH=/data/littup/littup.db \
    LITTUP_PROJECTS_DIR=/data/littup/projects

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl --fail "http://127.0.0.1:${PORT}/_stcore/health" || exit 1

CMD ["./start.sh"]

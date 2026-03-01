from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LittUpSettings:
    env: str
    log_level: str
    host: str
    port: int
    api_host: str
    api_port: int
    data_dir: Path
    db_path: Path
    projects_dir: Path

    @property
    def api_base_url(self) -> str:
        return f"http://{self.api_host}:{self.api_port}"


def _as_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def get_settings() -> LittUpSettings:
    env = os.getenv("LITTUP_ENV", "development").lower()
    host_default = "0.0.0.0" if env == "production" else "127.0.0.1"
    host = os.getenv("HOST", host_default)
    port = _as_int("PORT", 8501)

    api_host = os.getenv("LITTUP_API_HOST", "127.0.0.1")
    api_port = _as_int("LITTUP_API_PORT", 8756)

    data_dir = Path(os.getenv("LITTUP_DATA_DIR", Path.home() / ".littup")).expanduser().resolve()
    db_path = Path(os.getenv("LITTUP_DB_PATH", data_dir / "littup.db")).expanduser().resolve()
    projects_dir = Path(os.getenv("LITTUP_PROJECTS_DIR", data_dir / "projects")).expanduser().resolve()

    return LittUpSettings(
        env=env,
        log_level=os.getenv("LITTUP_LOG_LEVEL", "info"),
        host=host,
        port=port,
        api_host=api_host,
        api_port=api_port,
        data_dir=data_dir,
        db_path=db_path,
        projects_dir=projects_dir,
    )


def ensure_storage_paths(settings: LittUpSettings | None = None) -> LittUpSettings:
    settings = settings or get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.projects_dir.mkdir(parents=True, exist_ok=True)
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    return settings

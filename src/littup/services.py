from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from sqlalchemy import select

from .config import ensure_storage_paths, get_settings
from .db import db_session
from .models import AgentMessage, Memory, Project, Snapshot

ROLES = ["Planner", "Coder", "Tester", "Reviewer", "Documenter"]
DEFAULT_TEAM_ASSIGNMENT = {
    "Planner": "Strategos",
    "Coder": "Builder-01",
    "Tester": "Guardian-QA",
    "Reviewer": "Eagle-Eye",
    "Documenter": "Lorekeeper",
}

settings = ensure_storage_paths(get_settings())
ROOT_DIR = settings.projects_dir
ROOT_DIR.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    from .db import Base, engine

    Base.metadata.create_all(bind=engine)


def list_projects() -> list[Project]:
    with db_session() as s:
        return list(s.scalars(select(Project).order_by(Project.updated_at.desc())).all())


def create_project(name: str, template: str, team_name: str = "Core Team") -> Project:
    with db_session() as s:
        project = Project(name=name, template=template, team_name=team_name, status="active")
        s.add(project)
        s.flush()
        project_id = project.id

    setup_project_files(project_id, template)
    save_snapshot(project_id, "Initial template scaffold")
    with db_session() as s:
        return s.get(Project, project_id)


def get_project(project_id: int) -> Project | None:
    with db_session() as s:
        return s.get(Project, project_id)


def get_project_path(project_id: int) -> Path:
    path = ROOT_DIR / f"project_{project_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def setup_project_files(project_id: int, template: str) -> None:
    here = Path(__file__).resolve().parents[2]
    src = here / "templates" / template
    dst = get_project_path(project_id)
    if src.exists() and not any(dst.iterdir()):
        shutil.copytree(src, dst, dirs_exist_ok=True)


def list_project_files(project_id: int) -> list[str]:
    project_path = get_project_path(project_id)
    files: list[str] = []
    for item in sorted(project_path.rglob("*")):
        if item.is_file():
            files.append(str(item.relative_to(project_path)))
    return files


def read_file(project_id: int, rel_path: str) -> str:
    target = get_project_path(project_id) / rel_path
    return target.read_text(encoding="utf-8") if target.exists() else ""


def write_file(project_id: int, rel_path: str, content: str) -> None:
    target = get_project_path(project_id) / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def add_message(project_id: int, role: str, content: str) -> None:
    with db_session() as s:
        s.add(AgentMessage(project_id=project_id, role=role, content=content))
        s.add(Memory(project_id=project_id, source="Memoria", content=f"{role}: {content}"))


def get_messages(project_id: int) -> list[AgentMessage]:
    with db_session() as s:
        return list(s.scalars(select(AgentMessage).where(AgentMessage.project_id == project_id).order_by(AgentMessage.created_at)).all())


def save_snapshot(project_id: int, note: str) -> Snapshot:
    project_path = get_project_path(project_id)
    state = {}
    for rel in list_project_files(project_id):
        state[rel] = read_file(project_id, rel)
    with db_session() as s:
        snap = Snapshot(project_id=project_id, note=note, content=json.dumps(state))
        s.add(snap)
        s.flush()
        return snap


def get_snapshots(project_id: int) -> list[Snapshot]:
    with db_session() as s:
        return list(s.scalars(select(Snapshot).where(Snapshot.project_id == project_id).order_by(Snapshot.created_at.desc())).all())


def evolve_project(project_id: int, feedback: str) -> str:
    planner_update = f"Roadmap evolved with feedback: {feedback}"
    add_message(project_id, "Planner", planner_update)
    add_message(project_id, "Reviewer", "Requested another quality and architecture pass.")
    save_snapshot(project_id, f"Evolution: {feedback[:60]}")
    return planner_update


def run_local_command(project_id: int, command: str) -> tuple[int, str]:
    allowed = {"python", "pytest", "bash", "sh"}
    if command.split()[0] not in allowed:
        return 1, "Command blocked by local sandbox policy."

    workdir = get_project_path(project_id)
    with tempfile.TemporaryDirectory(prefix="littup-run-") as sandbox:
        sb = Path(sandbox)
        shutil.copytree(workdir, sb / "project", dirs_exist_ok=True)
        proc = subprocess.run(
            command,
            shell=True,
            cwd=sb / "project",
            capture_output=True,
            text=True,
            timeout=30,
        )
        return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()


def triad_integrations() -> dict[str, str]:
    return {
        "Agentora": "Agent roster can be imported and mapped to Forge roles.",
        "Memoria": "Every chat turn and snapshot summary is auto-synced as local memory.",
        "Launchpad": "Package project folder + metadata manifest for one-click registration.",
    }

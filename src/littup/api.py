from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import ensure_storage_paths, get_settings
from .services import (
    add_message,
    create_project,
    evolve_project,
    get_messages,
    get_project,
    get_snapshots,
    init_db,
    list_projects,
    triad_integrations,
)

settings = ensure_storage_paths(get_settings())

app = FastAPI(title="LittUp API", version="0.2.0")


class ProjectIn(BaseModel):
    name: str
    template: str
    team_name: str = "Core Team"


class MessageIn(BaseModel):
    role: str
    content: str


class EvolveIn(BaseModel):
    feedback: str


@app.on_event("startup")
def startup() -> None:
    ensure_storage_paths(settings)
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "local-first", "env": settings.env}


@app.get("/projects")
def projects() -> list[dict]:
    return [
        {
            "id": p.id,
            "name": p.name,
            "status": p.status,
            "template": p.template,
            "updated_at": p.updated_at.isoformat(),
            "team_name": p.team_name,
        }
        for p in list_projects()
    ]


@app.post("/projects")
def create(payload: ProjectIn) -> dict:
    p = create_project(payload.name, payload.template, payload.team_name)
    return {"id": p.id, "name": p.name}


@app.get("/projects/{project_id}/chat")
def chat(project_id: int) -> list[dict]:
    if not get_project(project_id):
        raise HTTPException(404, "Project not found")
    return [{"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in get_messages(project_id)]


@app.post("/projects/{project_id}/chat")
def add_chat(project_id: int, payload: MessageIn) -> dict:
    if not get_project(project_id):
        raise HTTPException(404, "Project not found")
    add_message(project_id, payload.role, payload.content)
    return {"ok": True}


@app.post("/projects/{project_id}/evolve")
def evolve(project_id: int, payload: EvolveIn) -> dict:
    if not get_project(project_id):
        raise HTTPException(404, "Project not found")
    return {"message": evolve_project(project_id, payload.feedback)}


@app.get("/projects/{project_id}/history")
def history(project_id: int) -> list[dict]:
    if not get_project(project_id):
        raise HTTPException(404, "Project not found")
    return [{"id": s.id, "note": s.note, "created_at": s.created_at.isoformat()} for s in get_snapshots(project_id)]


@app.get("/integrations")
def integrations() -> dict[str, str]:
    return triad_integrations()

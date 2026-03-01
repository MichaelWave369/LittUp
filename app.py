from __future__ import annotations

import requests
import streamlit as st

from littup.config import ensure_storage_paths, get_settings
from littup.services import (
    DEFAULT_TEAM_ASSIGNMENT,
    ROLES,
    add_message,
    create_project,
    evolve_project,
    get_messages,
    get_snapshots,
    init_db,
    list_project_files,
    list_projects,
    read_file,
    run_local_command,
    save_snapshot,
    triad_integrations,
    write_file,
)

settings = ensure_storage_paths(get_settings())

st.set_page_config(page_title="LittUp v0.2", layout="wide", page_icon="🛠️")


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {background: linear-gradient(120deg, #0a0a0f 0%, #15152a 100%); color: #f7f7ff;}
        .stMarkdown, .stText, .st-emotion-cache-1v0mbdj {color: #f7f7ff;}
        .block-card {background: rgba(21, 21, 42, 0.75); border:1px solid #2a2a4d; border-radius:16px; padding:1rem;}
        .role-chip {padding:0.25rem 0.5rem; border-radius:12px; background:#302d63; margin:0.15rem; display:inline-block;}
        .accent {color:#7ae7ff;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard() -> None:
    st.subheader("Project Dashboard")
    projects = list_projects()
    if not projects:
        st.info("No projects yet. Create your first local forge project.")
    for p in projects:
        st.markdown(
            f"<div class='block-card'><b>{p.name}</b> · {p.template} · {p.status}<br/>"
            f"Team: {p.team_name}<br/>Last modified: {p.updated_at}</div>",
            unsafe_allow_html=True,
        )

    with st.expander("➕ New Project", expanded=True):
        name = st.text_input("Project name", value="My Local Forge")
        template = st.selectbox("Template", ["web_app", "python_script", "game"])
        team = st.text_input("Agent Team Name", value="Triad Build Squad")
        if st.button("Create Project", type="primary"):
            create_project(name, template, team)
            st.success("Project created.")
            st.rerun()


def render_forge_room() -> None:
    st.subheader("Multi-Agent Forge Room")
    projects = list_projects()
    if not projects:
        st.warning("Create a project first.")
        return

    selection = st.selectbox("Choose Project", projects, format_func=lambda p: f"#{p.id} {p.name}")
    project_id = selection.id

    st.markdown("#### Team Roles")
    cols = st.columns(len(ROLES))
    role_map = st.session_state.setdefault("role_map", DEFAULT_TEAM_ASSIGNMENT.copy())
    for idx, role in enumerate(ROLES):
        with cols[idx]:
            role_map[role] = st.text_input(role, value=role_map.get(role, ""), key=f"role_{role}")

    st.markdown("#### Live Collaboration Chat")
    for msg in get_messages(project_id):
        st.chat_message(msg.role).write(msg.content)

    user_msg = st.chat_input("Coordinate your team...")
    if user_msg:
        add_message(project_id, "Planner", user_msg)
        add_message(project_id, "Coder", "Drafted initial implementation path based on planner brief.")
        add_message(project_id, "Tester", "Prepared sanity checks and regression plan.")
        add_message(project_id, "Reviewer", "Will evaluate quality gate once commit-ready.")
        add_message(project_id, "Documenter", "README updates queued for latest architecture.")
        st.rerun()

    st.markdown("#### Code Workspace")
    files = list_project_files(project_id)
    if not files:
        st.info("Template has no files yet.")
        return

    file_choice = st.selectbox("File", files)
    source = read_file(project_id, file_choice)
    edited = st.text_area("Editor", value=source, height=320)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save"):
            write_file(project_id, file_choice, edited)
            save_snapshot(project_id, f"Edited {file_choice}")
            st.success("Saved and snapshotted.")
    with col2:
        if st.button("▶️ Run"):
            code, out = run_local_command(project_id, "python main.py")
            st.code(out or f"Exited with {code}")
    with col3:
        if st.button("🧪 Test"):
            code, out = run_local_command(project_id, "pytest -q")
            st.code(out or f"Exited with {code}")

    st.markdown("#### History & Evolution")
    feedback = st.text_input("Evolution feedback")
    if st.button("Evolve"):
        st.success(evolve_project(project_id, feedback or "General improvements"))

    for snap in get_snapshots(project_id)[:10]:
        st.caption(f"{snap.created_at} — {snap.note}")


def render_integrations() -> None:
    st.subheader("Triad369 Integrations")
    integrations = triad_integrations()
    for name, desc in integrations.items():
        st.markdown(f"- **{name}**: {desc}")


def api_health_status() -> str:
    try:
        response = requests.get(f"{settings.api_base_url}/health", timeout=0.5)
        if response.ok:
            return "✅ API companion running"
    except requests.RequestException:
        pass
    return "⚠️ API companion unavailable"


def render_sidebar() -> None:
    st.sidebar.title("LittUp v0.2")
    st.sidebar.caption("Local AI Code Forge · Private by default")
    st.sidebar.markdown("### Launchpad Readiness")
    st.sidebar.success("✅ Local-first")
    st.sidebar.success("✅ SQLite memory")
    st.sidebar.success("✅ Agentora-compatible roles")
    st.sidebar.caption(api_health_status())
    st.sidebar.caption(f"Data dir: {settings.data_dir}")


def main() -> None:
    init_db()
    inject_css()
    render_sidebar()
    st.title("🛠️ LittUp — The Local AI Code Forge")
    tabs = st.tabs(["Dashboard", "Forge Room", "Integrations"])
    with tabs[0]:
        render_dashboard()
    with tabs[1]:
        render_forge_room()
    with tabs[2]:
        render_integrations()


if __name__ == "__main__":
    main()

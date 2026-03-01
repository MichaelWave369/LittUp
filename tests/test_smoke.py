import importlib
import importlib.util
from pathlib import Path


def test_import_app_module():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location("littup_app", app_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    assert hasattr(module, "main")


def test_db_init_and_project_flow():
    services = importlib.import_module("littup.services")

    services.init_db()
    project = services.create_project("Smoke Project", "python_script", "QA Team")
    assert project.id is not None

    files = services.list_project_files(project.id)
    assert "main.py" in files

    services.write_file(project.id, "main.py", "print('smoke')\n")
    assert "smoke" in services.read_file(project.id, "main.py")


def test_api_health_route_and_handler():
    api = importlib.import_module("littup.api")

    paths = {route.path for route in api.app.routes}
    assert "/health" in paths

    body = api.health()
    assert body["status"] == "ok"
    assert body["mode"] == "local-first"

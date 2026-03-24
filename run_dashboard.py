#!/usr/bin/env python3
"""
Cross-platform launcher for the BioSync Tele-Rescue stack.
Starts the FastAPI backend and Streamlit frontend together.
"""
from __future__ import annotations

import json
import socket
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


REPO_ROOT = Path(__file__).resolve().parent
VENV_DIR = REPO_ROOT / ".venv"
BACKEND_HEALTH_URL = "http://127.0.0.1:8000/health"
BACKEND_OPENAPI_URL = "http://127.0.0.1:8000/openapi.json"
EXPECTED_BACKEND_SERVICE = "BioSync Tele-Rescue Backend"
REQUIRED_BACKEND_PATHS = {"/auth/login", "/auth/register"}
DEFAULT_DASHBOARD_PORT = 8501
MAX_DASHBOARD_PORT = 8510


def _venv_python() -> str:
    """Return the path to the venv Python executable, creating the venv if needed."""
    venv_python = VENV_DIR / "bin" / "python"
    if not venv_python.exists():
        print(f"Creating virtual environment at {VENV_DIR} ...")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    return str(venv_python)


def install_dependencies() -> None:
    python = _venv_python()
    subprocess.check_call([python, "-m", "pip", "install", "--upgrade", "pip"], cwd=REPO_ROOT)
    subprocess.check_call([python, "-m", "pip", "install", "-r", "requirements.txt"], cwd=REPO_ROOT)
    subprocess.check_call([python, "-m", "pip", "install", "-r", "backend/requirements.txt"], cwd=REPO_ROOT)


def _is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def _pick_dashboard_port() -> int:
    for port in range(DEFAULT_DASHBOARD_PORT, MAX_DASHBOARD_PORT + 1):
        if _is_port_free(port):
            return port
    raise RuntimeError(
        f"No free dashboard port found in range {DEFAULT_DASHBOARD_PORT}-{MAX_DASHBOARD_PORT}."
    )


def _build_backend_cmd() -> list[str]:
    python = _venv_python()
    return [python, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


def _build_frontend_cmd(port: int) -> list[str]:
    python = _venv_python()
    return [
        python,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.headless",
        "true",
        "--server.port",
        str(port),
    ]


def _load_json(url: str, timeout_seconds: float = 1.5) -> dict:
    with urlopen(url, timeout=timeout_seconds) as response:
        if response.status != 200:
            raise RuntimeError(f"{url} returned HTTP {response.status}")
        return json.load(response)


def probe_backend() -> tuple[str, str]:
    try:
        health_payload = _load_json(BACKEND_HEALTH_URL)
    except URLError:
        return "absent", ""
    except Exception as exc:
        return "incompatible", f"Unable to read backend health endpoint: {exc}"

    if health_payload.get("service") != EXPECTED_BACKEND_SERVICE:
        return "incompatible", (
            f"Unexpected service is listening on 127.0.0.1:8000: {health_payload!r}"
        )

    try:
        openapi_payload = _load_json(BACKEND_OPENAPI_URL)
    except Exception as exc:
        return "incompatible", f"Unable to read backend OpenAPI schema: {exc}"

    available_paths = set(openapi_payload.get("paths", {}))
    missing_paths = sorted(REQUIRED_BACKEND_PATHS - available_paths)
    if missing_paths:
        return "incompatible", (
            "Existing backend is missing required auth routes: "
            + ", ".join(missing_paths)
        )

    return "ready", ""


def wait_for_backend(
    timeout_seconds: float = 20.0,
    process: subprocess.Popen | None = None,
) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        status, detail = probe_backend()
        if status == "ready":
            return
        if status == "incompatible":
            raise RuntimeError(detail)
        if process is not None and process.poll() is not None:
            raise RuntimeError("FastAPI backend process exited before becoming ready.")
        time.sleep(0.5)
    raise RuntimeError("FastAPI backend did not become healthy in time.")


def terminate_process(process: subprocess.Popen | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def main() -> int:
    print("=" * 48)
    print("  BioSync Tele-Rescue")
    print("  Starting backend + dashboard")
    print("=" * 48)
    print()

    if not (REPO_ROOT / "app.py").exists():
        print("ERROR: app.py not found.")
        return 1

    print("Installing/updating dependencies...")
    install_dependencies()

    backend_process: subprocess.Popen | None = None
    frontend_process: subprocess.Popen | None = None

    def cleanup(*_args):
        terminate_process(frontend_process)
        terminate_process(backend_process)

    def handle_signal(signum, frame):
        cleanup()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        backend_status, backend_detail = probe_backend()
        if backend_status == "ready":
            print("Using existing FastAPI backend on http://127.0.0.1:8000 ...")
        elif backend_status == "incompatible":
            raise RuntimeError(
                backend_detail
                + " Stop the process using port 8000 or start this repository with `bash start.sh`."
            )
        else:
            print("Starting FastAPI backend on http://127.0.0.1:8000 ...")
            backend_process = subprocess.Popen(_build_backend_cmd(), cwd=REPO_ROOT)
            wait_for_backend(process=backend_process)

        dashboard_port = _pick_dashboard_port()
        if dashboard_port != DEFAULT_DASHBOARD_PORT:
            print(
                f"Port {DEFAULT_DASHBOARD_PORT} is busy, using dashboard port {dashboard_port} instead ..."
            )

        print(f"Starting Streamlit dashboard on http://127.0.0.1:{dashboard_port} ...")
        print("Press Ctrl+C to stop both services.")
        frontend_process = subprocess.Popen(_build_frontend_cmd(dashboard_port), cwd=REPO_ROOT)

        while True:
            if backend_process is not None and backend_process.poll() is not None:
                raise RuntimeError("Backend process exited unexpectedly.")
            if frontend_process.poll() is not None:
                raise RuntimeError("Streamlit process exited unexpectedly.")
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()
        print("\nStopped.")
        return 0
    except Exception as exc:
        cleanup()
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

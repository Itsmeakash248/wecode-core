#!/usr/bin/env python3
"""
Cross-platform launcher for the BioSync Tele-Rescue stack.
Starts the FastAPI backend and Streamlit frontend together.
"""
from __future__ import annotations

import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


REPO_ROOT = Path(__file__).resolve().parent
BACKEND_URL = "http://127.0.0.1:8000/health"
BACKEND_CMD = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
FRONTEND_CMD = [
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "app.py",
    "--server.headless",
    "true",
    "--server.port",
    "8501",
]


def install_dependencies() -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=REPO_ROOT)


def wait_for_backend(timeout_seconds: float = 20.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urlopen(BACKEND_URL, timeout=1.5) as response:
                if response.status == 200:
                    return
        except URLError:
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
        print("Starting FastAPI backend on http://localhost:8000 ...")
        backend_process = subprocess.Popen(BACKEND_CMD, cwd=REPO_ROOT)
        wait_for_backend()

        print("Starting Streamlit dashboard on http://localhost:8501 ...")
        print("Press Ctrl+C to stop both services.")
        frontend_process = subprocess.Popen(FRONTEND_CMD, cwd=REPO_ROOT)

        while True:
            if backend_process.poll() is not None:
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

#!/bin/bash
# ============================================================
#  BioSync Tele-Rescue — One-Command Launcher
#  Starts: FastAPI backend (port 8000) + Streamlit UI (port 8501)
# ============================================================

set -e
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$REPO_DIR/.venv"

# ── 1. Check / create venv ──────────────────────────────────
if [ ! -d "$VENV" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv "$VENV"
fi

PYTHON="$VENV/bin/python"
PIP="$VENV/bin/pip"

# ── 2. Install all dependencies ─────────────────────────────
echo "📥 Installing dependencies..."
$PIP install -q -r "$REPO_DIR/requirements.txt"

# ── 3. Cleanup function (Ctrl+C kills both processes) ────────
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo ""
  echo "🛑 Shutting down..."
  [ -n "$BACKEND_PID" ]  && kill "$BACKEND_PID"  2>/dev/null
  [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null
  exit 0
}
trap cleanup SIGINT SIGTERM

# ── 4. Free ports if already in use ────────────────────────
for PORT in 8000 8501; do
  if fuser "$PORT/tcp" > /dev/null 2>&1; then
    echo "⚠️  Port $PORT in use — killing existing process..."
    fuser -k "$PORT/tcp" 2>/dev/null
    sleep 0.5
  fi
done

# ── 5. Start FastAPI backend ─────────────────────────────────
echo ""
echo "🚀 Starting FastAPI backend on http://localhost:8000 ..."
cd "$REPO_DIR"
"$VENV/bin/uvicorn" backend.main:app --host 0.0.0.0 --port 8000 --log-level warning &
BACKEND_PID=$!

# Wait for backend to be ready
echo -n "   Waiting for backend"
for i in $(seq 1 20); do
  sleep 0.5
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo " ✅"
    break
  fi
  echo -n "."
done

# ── 6. Start Streamlit frontend ──────────────────────────────
echo "🖥️  Starting Streamlit dashboard on http://localhost:8501 ..."
"$VENV/bin/streamlit" run "$REPO_DIR/app.py" \
  --server.port 8501 \
  --server.headless true \
  --server.address 0.0.0.0 \
  --browser.gatherUsageStats false &
FRONTEND_PID=$!

# ── 7. Summary ───────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  ✅ BioSync Tele-Rescue is running!"
echo ""
echo "  📡 Backend API  → http://localhost:8000"
echo "  📖 API Docs     → http://localhost:8000/docs"
echo "  🖥️  Dashboard   → http://localhost:8501"
echo ""
echo "  [Optional] Run vitals simulator in another terminal:"
echo "  source .venv/bin/activate && python -m backend.sim_data"
echo ""
echo "  Press Ctrl+C to stop everything."
echo "============================================================"
echo ""

# Keep alive
wait

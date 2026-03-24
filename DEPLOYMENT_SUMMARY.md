# BioSync Tele-Rescue — Deployment Summary

## What Was Done

Deployed the full-stack **BioSync Tele-Rescue** app (Streamlit + FastAPI + ML) to **Render.com** for free.

---

## Problem: Why Not Vercel?

Vercel only supports static/serverless apps. This project uses:
- **Streamlit** — requires a persistent Python server
- **FastAPI** — long-running backend with WebSockets
- **scikit-learn** — ML anomaly detection (Isolation Forest)
- **Ollama** — local LLM (not cloud-compatible)

**Solution: Render.com** — free tier, supports long-running Python processes.

---

## Changes Made

### 1. `backend/llm.py` — Replaced Ollama with Google Gemini
- Ollama runs locally only (can't run on cloud)
- Switched to **Google Gemini API** (`gemini-1.5-flash`) using the existing `GEMINI_API_KEY`
- Graceful fallback still works if API key is missing

### 2. `render.yaml` — Render Blueprint (new file)
Defines two free services:
| Service | Type | Start Command |
|---------|------|---------------|
| `biosync-backend` | FastAPI | `uvicorn backend.main:app` |
| `biosync-frontend` | Streamlit | `streamlit run app.py` |

### 3. `frontend-requirements.txt` — Lean frontend deps (new file)
- Root `requirements.txt` was pulling ALL backend packages (scikit-learn, numpy, fastapi…) for the frontend
- Caused 10-15 min build hangs on Render free tier
- New `frontend-requirements.txt` only has what Streamlit needs: `streamlit`, `pandas`, `plotly`, `httpx`, `python-dotenv`, `requests`

### 4. `.streamlit/config.toml` — Headless cloud config (new file)
```toml
[server]
headless = true
enableCORS = false
```

### 5. `backend/requirements.txt`
- Added `google-generativeai` package

### 6. `.env.example` — Updated
Documents all required environment variables.

---

## Deploy Steps (Render.com)

1. Go to [render.com](https://render.com) → **New + → Blueprint**
2. Connect `Itsmeakash248/wecode-core` repo
3. Set env vars after services are created:

**`biosync-backend` service:**
| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | *(your Gemini API key)* |

**`biosync-frontend` service:**
| Key | Value |
|-----|-------|
| `BIOSYNC_API_URL` | `https://biosync-backend.onrender.com` |

4. Verify:
   - Backend: `https://biosync-backend.onrender.com/health`
   - Frontend: `https://biosync-frontend.onrender.com`

---

## Notes

- **Free tier sleep**: Services sleep after 15 min of inactivity — first request takes ~30s to wake up
- **WebRTC video calls**: Work via browser-native JS (no `streamlit-webrtc` needed)
- **`BIOSYNC_API_URL`** env var in `components/platform_api.py` already existed — no code change needed for frontend → backend wiring

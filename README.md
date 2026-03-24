<p align="center">
  <video src="animation.mp4" width="386" autoplay loop muted playsinline>
    <a href="animation.mp4">Animated logo</a>
  </video>
</p>

<h1 align="center">BioSync Tele-Rescue</h1>
<p align="center">
  AI-assisted teleconsultation platform for emergency healthcare monitoring and doctor availability.
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#backend-api">Backend API</a> •
  <a href="#project-structure">Project Structure</a>
</p>

## Overview

BioSync Tele-Rescue is a healthcare platform prototype built for rapid teleconsultation workflows. It combines a Streamlit-based dashboard with a FastAPI backend to support:

- Patient vitals intake
- Anomaly detection and triage brief generation
- Doctor availability and appointment booking
- Real-time event broadcasting for monitoring workflows

## Features

- Streamlit multi-view application:
  - Home
  - Patient Dashboard
  - Doctor Platform
- FastAPI backend endpoints for:
  - Vitals ingestion and anomaly detection
  - Doctor listing and status updates
  - Appointment booking and retrieval
  - Notifications and feedback
- WebSocket broadcast channel for live updates
- Simulated vitals stream generator for testing and demos

## Tech Stack

- Frontend/UI: Streamlit, Plotly
- Backend/API: FastAPI, Uvicorn, Pydantic
- ML Utilities: scikit-learn (anomaly support)
- Data and Utilities: pandas, numpy, httpx

## Quick Start

### 1) Prerequisites

- Python 3.8+
- pip

### 2) Install dashboard dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the dashboard

Use any one of the following:

```bash
# Windows
run_dashboard.bat

# Cross-platform Python launcher
python run_dashboard.py

# Direct Streamlit run
streamlit run app.py
```

Default dashboard URL:

- http://localhost:8501

## Backend API

### 1) Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 2) Run the API server

```bash
uvicorn backend.main:app --reload --port 8000
```

### 3) Optional: run vitals simulator

```bash
python -m backend.sim_data
```

### 4) API documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Core Endpoints

- GET /health
- POST /vitals
- GET /ws
- GET /doctors
- GET /doctors/{doctor_id}
- PATCH /doctors/{doctor_id}/status
- POST /appointments
- GET /appointments/{appt_id}
- GET /notifications/{uid}
- PATCH /notifications/{uid}/{notif_id}/read
- POST /feedback
- GET /feedback/{doctor_id}

## Project Structure

```text
wecode-core/
├── app.py
├── README.md
├── requirements.txt
├── run_dashboard.py
├── run_dashboard.bat
├── run_dashboard.sh
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── llm.py
│   ├── sim_data.py
│   ├── requirements.txt
│   └── ml/
│       └── anomaly.py
├── components/
│   ├── data_manager.py
│   ├── pages.py
│   ├── ui_components.py
│   └── webrtc_consultation.py
└── test_components.py
```

## Testing

```bash
python test_components.py
```

## Notes

- This repository currently uses in-memory backend stores for appointments, notifications, and feedback.
- For production deployment, replace in-memory storage with a persistent datastore and tighten CORS, auth, and observability controls.

## License

No license file is currently included. Add a license before public distribution.

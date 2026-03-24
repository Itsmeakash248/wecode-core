"""
FastAPI backend — BioSync Tele-Rescue
Healthcare PS 1 · Doctor Availability & Teleconsultation Platform

Endpoints
---------
POST  /vitals              — Ingest patient vitals, run anomaly detection
GET   /ws                  — WebSocket: live vitals feed for doctor dashboard
GET   /doctors             — List available doctors
POST  /appointments        — Book a teleconsultation appointment
GET   /appointments/{id}   — Get appointment by ID
GET   /notifications/{uid} — Get notifications for a user
POST  /feedback            — Submit patient feedback
GET   /health              — Health check
"""

import uuid
from datetime import datetime, timezone
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import (
    VitalsPayload, AnomalyEvent,
    Doctor, AppointmentRequest, Appointment,
    Notification, FeedbackRequest, Feedback,
)
from backend.ml.anomaly import detect
from backend.llm import get_triage_brief


# ─── In-memory stores (replace with a real DB for production) ─────────────────

DOCTORS: List[Doctor] = [
    Doctor(id="d1", name="Dr. Priya Sharma",   specialty="Cardiologist",       status="available", rating=4.9),
    Doctor(id="d2", name="Dr. Rajan Mehta",    specialty="General Physician",  status="available", rating=4.7),
    Doctor(id="d3", name="Dr. Ananya Bose",    specialty="Emergency Medicine", status="available", rating=4.8),
    Doctor(id="d4", name="Dr. Vikram Singh",   specialty="Pulmonologist",      status="busy",      rating=4.6),
    Doctor(id="d5", name="Dr. Sunita Reddy",   specialty="Neurologist",        status="offline",   rating=4.5),
]

appointments: dict[str, Appointment] = {}
notifications: dict[str, List[Notification]] = {}   # uid -> list
feedbacks: dict[str, Feedback] = {}


# ─── WebSocket connection manager ─────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.remove(ws)


manager = ConnectionManager()


# ─── App factory ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ BioSync backend starting — Isolation Forest loaded.")
    yield
    print("🛑 BioSync backend shutting down.")

app = FastAPI(
    title="BioSync Tele-Rescue API",
    description=(
        "Healthcare PS 1 — Doctor Availability & Teleconsultation Platform. "
        "Edge-AI wearable vitals → anomaly detection → auto-dial emergency doctor."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Meta"])
def health():
    return {"status": "ok", "service": "BioSync Tele-Rescue Backend"}


# ─── Vitals ingestion + anomaly detection ─────────────────────────────────────

@app.post("/vitals", response_model=AnomalyEvent, tags=["Vitals & Anomaly"])
async def ingest_vitals(payload: VitalsPayload):
    """
    Accepts patient vitals, runs Isolation Forest + clinical threshold check,
    generates an LLM triage brief on anomaly, and broadcasts to WS subscribers.
    """
    if payload.timestamp is None:
        payload.timestamp = datetime.now(timezone.utc).isoformat()

    is_anomaly, score = detect(payload)

    triage_brief = ""
    if is_anomaly:
        triage_brief = get_triage_brief(payload, score)

    event = AnomalyEvent(
        vitals=payload,
        anomaly_score=score,
        is_anomaly=is_anomaly,
        triage_brief=triage_brief,
    )

    # Broadcast to all connected doctor dashboards
    await manager.broadcast(event.model_dump())

    return event


# ─── WebSocket — live doctor dashboard feed ────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Connect here to receive real-time vitals frames and anomaly events.
    Intended for the Doctor Dashboard (Streamlit or any WS client).
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; data is pushed via broadcast()
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ─── Doctor listing & availability ────────────────────────────────────────────

@app.get("/doctors", response_model=List[Doctor], tags=["Doctor Availability"])
def list_doctors(status: str = None):
    """Return all doctors, optionally filtered by status (available/busy/offline)."""
    if status:
        return [d for d in DOCTORS if d.status == status]
    return DOCTORS


@app.get("/doctors/{doctor_id}", response_model=Doctor, tags=["Doctor Availability"])
def get_doctor(doctor_id: str):
    for d in DOCTORS:
        if d.id == doctor_id:
            return d
    raise HTTPException(status_code=404, detail="Doctor not found")


@app.patch("/doctors/{doctor_id}/status", response_model=Doctor, tags=["Doctor Availability"])
def update_doctor_status(doctor_id: str, status: str):
    """Update a doctor's availability status (available/busy/offline)."""
    for d in DOCTORS:
        if d.id == doctor_id:
            d.status = status
            return d
    raise HTTPException(status_code=404, detail="Doctor not found")


# ─── Appointment booking ───────────────────────────────────────────────────────

@app.post("/appointments", response_model=Appointment, tags=["Appointments"])
async def book_appointment(req: AppointmentRequest):
    """Book a teleconsultation appointment with an available doctor."""
    doctor = next((d for d in DOCTORS if d.id == req.doctor_id), None)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if doctor.status != "available":
        raise HTTPException(status_code=409, detail=f"Doctor is currently {doctor.status}")

    appt_id = str(uuid.uuid4())[:8]
    now     = datetime.now(timezone.utc).isoformat()

    appt = Appointment(
        **req.model_dump(),
        appointment_id=appt_id,
        status="confirmed",
        created_at=now,
    )
    appointments[appt_id] = appt

    # Mark doctor as busy
    doctor.status = "busy"

    # Create notification for patient
    _add_notification(
        uid=req.patient_id,
        message=f"Your appointment with {doctor.name} is confirmed (ID: {appt_id}).",
        notif_type="appointment",
    )
    # Create notification for doctor
    _add_notification(
        uid=req.doctor_id,
        message=f"New appointment with patient {req.patient_name} (ID: {appt_id}).",
        notif_type="appointment",
    )

    # Broadcast appointment event to WS
    await manager.broadcast({"event": "appointment_booked", "appointment": appt.model_dump()})
    return appt


@app.get("/appointments/{appt_id}", response_model=Appointment, tags=["Appointments"])
def get_appointment(appt_id: str):
    if appt_id not in appointments:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointments[appt_id]


# ─── Notifications ────────────────────────────────────────────────────────────

@app.get("/notifications/{uid}", response_model=List[Notification], tags=["Notifications"])
def get_notifications(uid: str):
    """Get all notifications for a patient or doctor by their ID."""
    return notifications.get(uid, [])


@app.patch("/notifications/{uid}/{notif_id}/read", tags=["Notifications"])
def mark_notification_read(uid: str, notif_id: str):
    for n in notifications.get(uid, []):
        if n.notification_id == notif_id:
            n.read = True
            return {"status": "marked_read"}
    raise HTTPException(status_code=404, detail="Notification not found")


# ─── Patient feedback ─────────────────────────────────────────────────────────

@app.post("/feedback", response_model=Feedback, tags=["Feedback"])
def submit_feedback(req: FeedbackRequest):
    """Submit patient feedback and rating for a doctor after consultation."""
    if not (1 <= req.rating <= 5):
        raise HTTPException(status_code=422, detail="Rating must be between 1 and 5")

    fb_id = str(uuid.uuid4())[:8]
    now   = datetime.now(timezone.utc).isoformat()

    feedback = Feedback(**req.model_dump(), feedback_id=fb_id, created_at=now)
    feedbacks[fb_id] = feedback

    # Update doctor's average rating (simple rolling avg)
    doctor = next((d for d in DOCTORS if d.id == req.doctor_id), None)
    if doctor:
        all_ratings = [f.rating for f in feedbacks.values() if f.doctor_id == doctor.id]
        doctor.rating = round(sum(all_ratings) / len(all_ratings), 2)

    return feedback


@app.get("/feedback/{doctor_id}", response_model=List[Feedback], tags=["Feedback"])
def get_doctor_feedback(doctor_id: str):
    return [f for f in feedbacks.values() if f.doctor_id == doctor_id]


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _add_notification(uid: str, message: str, notif_type: str):
    notif = Notification(
        notification_id=str(uuid.uuid4())[:8],
        recipient_id=uid,
        message=message,
        type=notif_type,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    notifications.setdefault(uid, []).append(notif)

"""
FastAPI backend for the BioSync Tele-Rescue telemedicine platform.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.llm import get_triage_brief
from backend.ml.anomaly import detect
from backend.models import (
    AnomalyEvent,
    AuthResponse,
    Appointment,
    AppointmentRequest,
    AppointmentUpdateRequest,
    Doctor,
    DoctorStatusUpdateRequest,
    Feedback,
    FeedbackRequest,
    FeedbackSummary,
    LoginRequest,
    Notification,
    PatientProfile,
    RegisterRequest,
    VitalsPayload,
)
from backend.store import store


class ConnectionManager:
    def __init__(self) -> None:
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, payload: dict) -> None:
        disconnected: list[WebSocket] = []
        for websocket in self.active:
            try:
                await websocket.send_json(payload)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)


manager = ConnectionManager()


def _raise_http(exc: Exception) -> None:
    if isinstance(exc, KeyError):
        raise HTTPException(status_code=404, detail=str(exc).strip("'")) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    raise exc


async def _reminder_loop() -> None:
    while True:
        generated = store.generate_due_reminders()
        if generated:
            await manager.broadcast({"event": "reminders_generated", "count": generated})
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    reminder_task = asyncio.create_task(_reminder_loop())
    try:
        yield
    finally:
        reminder_task.cancel()
        with suppress(asyncio.CancelledError):
            await reminder_task


app = FastAPI(
    title="BioSync Tele-Rescue API",
    description="Doctor availability and teleconsultation platform backend.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Meta"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "BioSync Tele-Rescue Backend"}


@app.post("/auth/login", response_model=AuthResponse, tags=["Auth"])
def login(request: LoginRequest) -> AuthResponse:
    try:
        return store.login_user(request)
    except Exception as exc:  # pragma: no cover - mapped to HTTP
        _raise_http(exc)


@app.post("/auth/register", response_model=AuthResponse, tags=["Auth"])
def register(request: RegisterRequest) -> AuthResponse:
    try:
        return store.register_user(request)
    except Exception as exc:  # pragma: no cover - mapped to HTTP
        _raise_http(exc)


@app.post("/vitals", response_model=AnomalyEvent, tags=["Vitals & Anomaly"])
async def ingest_vitals(payload: VitalsPayload) -> AnomalyEvent:
    if payload.timestamp is None:
        payload.timestamp = datetime.now(timezone.utc).isoformat()

    is_anomaly, score = detect(payload)
    triage_brief = get_triage_brief(payload, score) if is_anomaly else ""

    event = AnomalyEvent(
        vitals=payload,
        anomaly_score=score,
        is_anomaly=is_anomaly,
        triage_brief=triage_brief,
    )
    await manager.broadcast({"event": "vitals", "payload": event.model_dump()})
    return event


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/patients", response_model=List[PatientProfile], tags=["Patients"])
def list_patients() -> list[PatientProfile]:
    return store.list_patients()


@app.get("/patients/{patient_id}", response_model=PatientProfile, tags=["Patients"])
def get_patient(patient_id: str) -> PatientProfile:
    try:
        return store.get_patient(patient_id)
    except Exception as exc:  # pragma: no cover - mapped to HTTP
        _raise_http(exc)


@app.get("/doctors", response_model=List[Doctor], tags=["Doctors"])
def list_doctors(status: Optional[str] = None) -> list[Doctor]:
    return store.list_doctors(status=status)


@app.get("/doctors/{doctor_id}", response_model=Doctor, tags=["Doctors"])
def get_doctor(doctor_id: str) -> Doctor:
    try:
        return store.get_doctor(doctor_id)
    except Exception as exc:  # pragma: no cover - mapped to HTTP
        _raise_http(exc)


@app.patch("/doctors/{doctor_id}/status", response_model=Doctor, tags=["Doctors"])
def update_doctor_status(doctor_id: str, request: DoctorStatusUpdateRequest) -> Doctor:
    try:
        return store.update_doctor_status(doctor_id, request.status)
    except Exception as exc:  # pragma: no cover - mapped to HTTP
        _raise_http(exc)


@app.post("/appointments", response_model=Appointment, tags=["Appointments"])
async def book_appointment(request: AppointmentRequest) -> Appointment:
    try:
        appointment = store.create_appointment(request)
    except Exception as exc:  # pragma: no cover - mapped to HTTP
        _raise_http(exc)

    await manager.broadcast({"event": "appointment_created", "appointment": appointment.model_dump()})
    return appointment


@app.get("/appointments", response_model=List[Appointment], tags=["Appointments"])
def list_appointments(
    user_id: Optional[str] = None,
    role: Optional[str] = Query(default=None, pattern="^(patient|doctor)$"),
    status: Optional[str] = None,
) -> list[Appointment]:
    return store.list_appointments(user_id=user_id, role=role, status=status)


@app.get("/appointments/{appointment_id}", response_model=Appointment, tags=["Appointments"])
def get_appointment(appointment_id: str) -> Appointment:
    try:
        return store.get_appointment(appointment_id)
    except Exception as exc:  # pragma: no cover - mapped to HTTP
        _raise_http(exc)


@app.patch("/appointments/{appointment_id}", response_model=Appointment, tags=["Appointments"])
async def update_appointment(appointment_id: str, request: AppointmentUpdateRequest) -> Appointment:
    try:
        appointment = store.update_appointment(appointment_id, request)
    except Exception as exc:  # pragma: no cover - mapped to HTTP
        _raise_http(exc)

    await manager.broadcast({"event": "appointment_updated", "appointment": appointment.model_dump()})
    return appointment


@app.get("/notifications/{uid}", response_model=List[Notification], tags=["Notifications"])
def get_notifications(uid: str, unread_only: bool = False) -> list[Notification]:
    return store.get_notifications(uid, unread_only=unread_only)


@app.patch("/notifications/{uid}/{notification_id}/read", tags=["Notifications"])
def mark_notification_read(uid: str, notification_id: str) -> dict[str, str]:
    try:
        store.mark_notification_read(uid, notification_id)
    except Exception as exc:  # pragma: no cover - mapped to HTTP
        _raise_http(exc)

    return {"status": "marked_read"}


@app.post("/notifications/process-reminders", tags=["Notifications"])
async def process_reminders() -> dict[str, int]:
    generated = store.generate_due_reminders()
    if generated:
        await manager.broadcast({"event": "reminders_generated", "count": generated})
    return {"generated": generated}


@app.post("/feedback", response_model=Feedback, tags=["Feedback"])
async def submit_feedback(request: FeedbackRequest) -> Feedback:
    try:
        feedback = store.submit_feedback(request)
    except Exception as exc:  # pragma: no cover - mapped to HTTP
        _raise_http(exc)

    await manager.broadcast({"event": "feedback_created", "feedback": feedback.model_dump()})
    return feedback


@app.get("/feedback", response_model=List[Feedback], tags=["Feedback"])
def list_feedback(
    doctor_id: Optional[str] = None,
    patient_id: Optional[str] = None,
) -> list[Feedback]:
    return store.list_feedback(doctor_id=doctor_id, patient_id=patient_id)


@app.get("/feedback/summary", response_model=FeedbackSummary, tags=["Feedback"])
def feedback_summary(
    doctor_id: Optional[str] = None,
    patient_id: Optional[str] = None,
) -> FeedbackSummary:
    return store.feedback_summary(doctor_id=doctor_id, patient_id=patient_id)

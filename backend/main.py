"""
FastAPI backend for the BioSync Tele-Rescue telemedicine platform.
"""
from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.consultation_auth import verify_consultation_token
from backend.consultation_page import render_consultation_page
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


class ConsultationConnectionManager:
    def __init__(self) -> None:
        self.rooms: dict[str, dict[str, Any]] = {}
        self.lock = asyncio.Lock()

    async def connect(
        self,
        room_id: str,
        participant_id: str,
        role: str,
        display_name: str,
        websocket: WebSocket,
    ) -> dict[str, Any]:
        await websocket.accept()

        async with self.lock:
            room = self.rooms.setdefault(
                room_id,
                {"connections": {}, "participants": {}, "messages": []},
            )
            room["connections"].setdefault(participant_id, []).append(websocket)
            room["participants"][participant_id] = {
                "participant_id": participant_id,
                "role": role,
                "display_name": display_name,
                "media_ready": False,
            }
            snapshot = {
                "participants": list(room["participants"].values()),
                "messages": list(room["messages"]),
            }

        await websocket.send_json(
            {
                "type": "room_state",
                "room_id": room_id,
                "participants": snapshot["participants"],
                "messages": snapshot["messages"],
            }
        )
        await self.broadcast(
            room_id,
            {
                "type": "participant_joined",
                "participant": {
                    "participant_id": participant_id,
                    "role": role,
                    "display_name": display_name,
                    "media_ready": False,
                },
                "participants": snapshot["participants"],
            },
            exclude_participant=participant_id,
        )
        return snapshot

    async def disconnect(self, room_id: str, participant_id: str, websocket: WebSocket) -> None:
        participants_snapshot: list[dict[str, Any]] | None = None

        async with self.lock:
            room = self.rooms.get(room_id)
            if room is None:
                return

            participant_connections = room["connections"].get(participant_id, [])
            if websocket in participant_connections:
                participant_connections.remove(websocket)

            if not participant_connections:
                room["connections"].pop(participant_id, None)
                room["participants"].pop(participant_id, None)
                participants_snapshot = list(room["participants"].values())

            if not room["connections"]:
                self.rooms.pop(room_id, None)

        if participants_snapshot is not None:
            await self.broadcast(
                room_id,
                {
                    "type": "participant_left",
                    "participant_id": participant_id,
                    "participants": participants_snapshot,
                },
            )

    async def handle_message(self, room_id: str, participant_id: str, payload: dict[str, Any]) -> None:
        message_type = payload.get("type")
        if message_type == "chat":
            await self._append_chat_message(room_id, participant_id, str(payload.get("message", "")))
            return

        if message_type == "media_state":
            await self._update_media_state(room_id, participant_id, bool(payload.get("media_ready")))
            return

        if message_type in {"offer", "answer", "ice_candidate", "hangup"}:
            await self._relay(room_id, participant_id, payload)
            return

        await self.send_to_participant(
            room_id,
            participant_id,
            {"type": "error", "message": f"Unsupported consultation message: {message_type}."},
        )

    async def send_to_participant(self, room_id: str, participant_id: str, payload: dict[str, Any]) -> None:
        async with self.lock:
            room = self.rooms.get(room_id)
            if room is None:
                return
            sockets = list(room["connections"].get(participant_id, []))

        disconnected: list[WebSocket] = []
        for websocket in sockets:
            try:
                await websocket.send_json(payload)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            await self.disconnect(room_id, participant_id, websocket)

    async def broadcast(
        self,
        room_id: str,
        payload: dict[str, Any],
        *,
        exclude_participant: str | None = None,
        target_participant: str | None = None,
    ) -> None:
        async with self.lock:
            room = self.rooms.get(room_id)
            if room is None:
                return

            targets: list[tuple[str, WebSocket]] = []
            for participant_id, sockets in room["connections"].items():
                if exclude_participant and participant_id == exclude_participant:
                    continue
                if target_participant and participant_id != target_participant:
                    continue
                for websocket in sockets:
                    targets.append((participant_id, websocket))

        disconnected: list[tuple[str, WebSocket]] = []
        for participant_id, websocket in targets:
            try:
                await websocket.send_json(payload)
            except Exception:
                disconnected.append((participant_id, websocket))

        for participant_id, websocket in disconnected:
            await self.disconnect(room_id, participant_id, websocket)

    async def _append_chat_message(self, room_id: str, participant_id: str, message: str) -> None:
        cleaned_message = message.strip()
        if not cleaned_message:
            return

        async with self.lock:
            room = self.rooms.get(room_id)
            if room is None:
                return

            participant = room["participants"].get(participant_id)
            if participant is None:
                return

            entry = {
                "participant_id": participant_id,
                "display_name": participant["display_name"],
                "role": participant["role"],
                "message": cleaned_message[:2000],
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
            room["messages"].append(entry)
            room["messages"] = room["messages"][-100:]

        await self.broadcast(room_id, {"type": "chat", "entry": entry})

    async def _update_media_state(self, room_id: str, participant_id: str, media_ready: bool) -> None:
        participants_snapshot: list[dict[str, Any]] | None = None

        async with self.lock:
            room = self.rooms.get(room_id)
            if room is None:
                return
            participant = room["participants"].get(participant_id)
            if participant is None:
                return
            participant["media_ready"] = media_ready
            participants_snapshot = list(room["participants"].values())

        await self.broadcast(
            room_id,
            {
                "type": "media_state",
                "participant_id": participant_id,
                "media_ready": media_ready,
                "participants": participants_snapshot,
            },
        )

    async def _relay(self, room_id: str, participant_id: str, payload: dict[str, Any]) -> None:
        async with self.lock:
            room = self.rooms.get(room_id)
            if room is None:
                return
            participant = room["participants"].get(participant_id)
            if participant is None:
                return

        outbound = {
            "type": payload.get("type"),
            "from": participant_id,
            "display_name": participant["display_name"],
            "role": participant["role"],
        }
        if "sdp" in payload:
            outbound["sdp"] = payload["sdp"]
        if "candidate" in payload:
            outbound["candidate"] = payload["candidate"]
        if "target" in payload:
            outbound["target"] = payload["target"]

        target_participant = payload.get("target")
        await self.broadcast(
            room_id,
            outbound,
            exclude_participant=participant_id if not target_participant else None,
            target_participant=target_participant,
        )


consultation_manager = ConsultationConnectionManager()


def _consultation_ice_servers() -> list[dict[str, Any]]:
    servers: list[dict[str, Any]] = [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
    ]

    turn_urls = [item.strip() for item in os.getenv("BIOSYNC_TURN_URL", "").split(",") if item.strip()]
    if turn_urls:
        turn_server: dict[str, Any] = {"urls": turn_urls}
        username = os.getenv("BIOSYNC_TURN_USERNAME")
        credential = os.getenv("BIOSYNC_TURN_PASSWORD")
        if username:
            turn_server["username"] = username
        if credential:
            turn_server["credential"] = credential
        servers.append(turn_server)

    return servers


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


def _validate_consultation_access(room_id: str, participant_id: str, role: str, token: str) -> dict[str, str]:
    normalized_role = role.strip().lower()
    if not verify_consultation_token(token, room_id, participant_id, normalized_role):
        raise HTTPException(status_code=403, detail="Invalid or expired consultation token.")

    try:
        return store.get_consultation_access_context(room_id, participant_id, normalized_role)
    except Exception as exc:  # pragma: no cover - mapped to HTTP
        _raise_http(exc)


@app.get("/consultations/{room_id}", response_class=HTMLResponse, tags=["Consultations"])
def consultation_room_page(
    room_id: str,
    participant_id: str = Query(...),
    role: str = Query(..., pattern="^(patient|doctor|Patient|Doctor)$"),
    token: str = Query(...),
    display_name: Optional[str] = Query(default=None),
) -> HTMLResponse:
    context = _validate_consultation_access(room_id, participant_id, role, token)
    participant_name = (display_name or "").strip() or context["participant_name"]
    html = render_consultation_page(
        room_id=room_id,
        participant_name=participant_name,
        participant_role=context["role"],
        participant_id=participant_id,
        token=token,
        ice_servers=_consultation_ice_servers(),
        turn_configured=bool(os.getenv("BIOSYNC_TURN_URL", "").strip()),
    )
    return HTMLResponse(content=html)


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


@app.websocket("/ws/consultations/{room_id}")
async def consultation_websocket(
    websocket: WebSocket,
    room_id: str,
    participant_id: str = Query(...),
    role: str = Query(...),
    token: str = Query(...),
    display_name: Optional[str] = Query(default=None),
) -> None:
    normalized_role = role.strip().lower()

    if not verify_consultation_token(token, room_id, participant_id, normalized_role):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        context = store.get_consultation_access_context(room_id, participant_id, normalized_role)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    participant_name = (display_name or "").strip() or context["participant_name"]
    await consultation_manager.connect(room_id, participant_id, normalized_role, participant_name, websocket)

    try:
        while True:
            payload = await websocket.receive_json()
            if isinstance(payload, dict):
                await consultation_manager.handle_message(room_id, participant_id, payload)
    except WebSocketDisconnect:
        await consultation_manager.disconnect(room_id, participant_id, websocket)
    except Exception:
        await consultation_manager.disconnect(room_id, participant_id, websocket)
        with suppress(Exception):
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


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

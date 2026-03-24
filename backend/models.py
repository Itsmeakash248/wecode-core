"""
Pydantic models for BioSync Tele-Rescue backend.
Aligned with Healthcare PS 1 — Doctor Availability & Teleconsultation Platform.
"""
from typing import Optional, Literal
from pydantic import BaseModel
from datetime import datetime


# ─── Vitals ──────────────────────────────────────────────────────────────────

class VitalsPayload(BaseModel):
    heart_rate: float           # bpm
    spo2: float                 # %
    accelerometer_x: float      # g-force
    accelerometer_y: float
    accelerometer_z: float
    timestamp: Optional[str] = None   # ISO-8601

    def is_critical(self) -> bool:
        return self.spo2 < 90 or self.heart_rate > 140 or self.heart_rate < 40


class AnomalyEvent(BaseModel):
    vitals: VitalsPayload
    anomaly_score: float
    is_anomaly: bool
    triage_brief: str


# ─── Doctor Availability ─────────────────────────────────────────────────────

class Doctor(BaseModel):
    id: str
    name: str
    specialty: str
    status: Literal["available", "busy", "offline"] = "available"
    rating: float = 4.5
    avatar_url: Optional[str] = None


# ─── Appointment Booking ─────────────────────────────────────────────────────

class AppointmentRequest(BaseModel):
    patient_name: str
    patient_id: str
    doctor_id: str
    symptoms: str
    preferred_time: Optional[str] = None   # ISO-8601


class Appointment(AppointmentRequest):
    appointment_id: str
    status: Literal["pending", "confirmed", "cancelled"] = "pending"
    created_at: str


# ─── Notifications ────────────────────────────────────────────────────────────

class Notification(BaseModel):
    notification_id: str
    recipient_id: str          # patient_id or doctor_id
    message: str
    type: Literal["appointment", "sos", "reminder", "feedback"]
    read: bool = False
    created_at: str


# ─── Patient Feedback ─────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_id: str
    rating: int                # 1–5
    comment: Optional[str] = None


class Feedback(FeedbackRequest):
    feedback_id: str
    created_at: str

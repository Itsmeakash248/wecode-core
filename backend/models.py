"""
Pydantic models for the BioSync Tele-Rescue backend.
"""
from typing import Optional, Literal

from pydantic import BaseModel, Field


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
    experience: int = 0
    avatar_url: Optional[str] = None


# ─── Patients ────────────────────────────────────────────────────────────────

class PatientProfile(BaseModel):
    id: str
    name: str
    age: int
    condition: str
    last_visit: Optional[str] = None
    risk_level: Literal["Low", "Medium", "High"] = "Low"


# ─── Authentication ──────────────────────────────────────────────────────────

UserRole = Literal["patient", "doctor"]


class AuthUser(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: UserRole
    linked_profile_id: str


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2)
    email: str
    password: str = Field(min_length=6)
    role: UserRole
    age: Optional[int] = Field(default=None, ge=0)
    condition: Optional[str] = None
    risk_level: Optional[Literal["Low", "Medium", "High"]] = None
    specialty: Optional[str] = None
    experience: Optional[int] = Field(default=None, ge=0)


class AuthResponse(BaseModel):
    user: AuthUser
    message: str


# ─── Appointment Booking ─────────────────────────────────────────────────────

class AppointmentRequest(BaseModel):
    patient_name: str
    patient_id: str
    doctor_id: str
    symptoms: str
    scheduled_time: Optional[str] = None   # ISO-8601
    consultation_type: str = "Consultation"


class Appointment(AppointmentRequest):
    appointment_id: str
    doctor_name: str
    consultation_room_id: str
    status: Literal["confirmed", "in_progress", "completed", "cancelled"] = "confirmed"
    created_at: str
    updated_at: str
    reminder_sent: bool = False


class AppointmentUpdateRequest(BaseModel):
    status: Optional[Literal["confirmed", "in_progress", "completed", "cancelled"]] = None
    scheduled_time: Optional[str] = None


class DoctorStatusUpdateRequest(BaseModel):
    status: Literal["available", "busy", "offline"]


# ─── Notifications ────────────────────────────────────────────────────────────

class Notification(BaseModel):
    notification_id: str
    recipient_id: str          # patient_id or doctor_id
    message: str
    type: Literal["appointment", "sos", "reminder", "feedback"]
    read: bool = False
    created_at: str
    appointment_id: Optional[str] = None


# ─── Patient Feedback ─────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_id: str
    rating: int = Field(ge=1, le=5)
    communication: int = Field(ge=1, le=5)
    wait_time: int = Field(ge=1, le=5)
    recommend: bool = True
    comment: Optional[str] = None


class Feedback(FeedbackRequest):
    feedback_id: str
    patient_name: str
    doctor_name: str
    created_at: str


class FeedbackSummary(BaseModel):
    total_feedback: int
    avg_rating: float
    avg_communication: float
    avg_wait_time: float
    recommend_percent: float
    low_ratings: int

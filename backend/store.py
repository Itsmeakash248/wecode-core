"""
Persistent JSON-backed store for the telemedicine platform.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Optional

from backend.models import (
    AuthResponse,
    AuthUser,
    Appointment,
    AppointmentRequest,
    AppointmentUpdateRequest,
    Doctor,
    Feedback,
    FeedbackRequest,
    FeedbackSummary,
    LoginRequest,
    Notification,
    PatientProfile,
    RegisterRequest,
)


DATA_PATH = Path(__file__).resolve().parent / "data" / "clinic_state.json"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_password(password: str, salt_hex: Optional[str] = None) -> tuple[str, str]:
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return salt.hex(), digest.hex()


def _verify_password(password: str, salt_hex: str, password_hash: str) -> bool:
    _, candidate_hash = _hash_password(password, salt_hex)
    return hmac.compare_digest(candidate_hash, password_hash)


def _email_local_part(name: str) -> str:
    cleaned = name.replace("Dr. ", "").replace("Dr.", "").strip().lower()
    slug = "".join(char if char.isalnum() else "." for char in cleaned)
    while ".." in slug:
        slug = slug.replace("..", ".")
    return slug.strip(".")


def _default_state() -> dict[str, Any]:
    return {
        "doctors": [
            {
                "id": "d1",
                "name": "Dr. Priya Sharma",
                "specialty": "Cardiology",
                "status": "available",
                "rating": 4.9,
                "experience": 12,
                "avatar_url": None,
                "current_appointment_id": None,
            },
            {
                "id": "d2",
                "name": "Dr. Rajan Mehta",
                "specialty": "General Medicine",
                "status": "available",
                "rating": 4.7,
                "experience": 9,
                "avatar_url": None,
                "current_appointment_id": None,
            },
            {
                "id": "d3",
                "name": "Dr. Ananya Bose",
                "specialty": "Emergency Medicine",
                "status": "available",
                "rating": 4.8,
                "experience": 14,
                "avatar_url": None,
                "current_appointment_id": None,
            },
            {
                "id": "d4",
                "name": "Dr. Vikram Singh",
                "specialty": "Pulmonology",
                "status": "busy",
                "rating": 4.6,
                "experience": 11,
                "avatar_url": None,
                "current_appointment_id": None,
            },
            {
                "id": "d5",
                "name": "Dr. Sunita Reddy",
                "specialty": "Neurology",
                "status": "offline",
                "rating": 4.5,
                "experience": 17,
                "avatar_url": None,
                "current_appointment_id": None,
            },
        ],
        "patients": [
            {
                "id": "p1",
                "name": "John Doe",
                "age": 45,
                "condition": "Hypertension",
                "last_visit": "2026-03-10T09:00:00+00:00",
                "risk_level": "Medium",
            },
            {
                "id": "p2",
                "name": "Sarah Wilson",
                "age": 32,
                "condition": "Cardiac Arrhythmia",
                "last_visit": "2026-03-14T11:00:00+00:00",
                "risk_level": "High",
            },
            {
                "id": "p3",
                "name": "Mike Johnson",
                "age": 58,
                "condition": "Diabetes",
                "last_visit": "2026-03-11T13:30:00+00:00",
                "risk_level": "Medium",
            },
            {
                "id": "p4",
                "name": "Emma Davis",
                "age": 29,
                "condition": "Anxiety",
                "last_visit": "2026-03-13T16:15:00+00:00",
                "risk_level": "Low",
            },
            {
                "id": "p5",
                "name": "Robert Brown",
                "age": 67,
                "condition": "COPD",
                "last_visit": "2026-03-09T08:45:00+00:00",
                "risk_level": "High",
            },
        ],
        "users": {},
        "appointments": {},
        "notifications": {},
        "feedbacks": {},
    }


class ClinicStore:
    def __init__(self, path: Path = DATA_PATH) -> None:
        self.path = path
        self.lock = RLock()
        self.state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            state = _default_state()
            self._seed_default_users(state)
            self.path.write_text(json.dumps(state, indent=2), encoding="utf-8")
            return state

        with self.path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)

        state = _default_state()
        state.update(raw)

        for doctor in state["doctors"]:
            doctor.setdefault("experience", 0)
            doctor.setdefault("avatar_url", None)
            doctor.setdefault("current_appointment_id", None)

        state.setdefault("users", {})
        migrated = self._seed_default_users(state)
        if migrated:
            with self.path.open("w", encoding="utf-8") as handle:
                json.dump(state, handle, indent=2)

        return state

    def _save_state(self) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self.state, handle, indent=2)

    def _build_user_record(
        self,
        *,
        email: str,
        full_name: str,
        role: str,
        linked_profile_id: str,
        password: str,
    ) -> dict[str, Any]:
        salt_hex, password_hash = _hash_password(password)
        return {
            "id": str(uuid.uuid4())[:8],
            "email": _normalize_email(email),
            "full_name": full_name,
            "role": role,
            "linked_profile_id": linked_profile_id,
            "password_salt": salt_hex,
            "password_hash": password_hash,
            "created_at": _utc_now_iso(),
        }

    def _seed_default_users(self, state: dict[str, Any]) -> bool:
        changed = False
        existing_emails = {
            _normalize_email(user["email"])
            for user in state.get("users", {}).values()
            if isinstance(user, dict) and user.get("email")
        }

        for patient in state["patients"]:
            email = f"{_email_local_part(patient['name'])}@biosync.local"
            if email in existing_emails:
                continue
            user = self._build_user_record(
                email=email,
                full_name=patient["name"],
                role="patient",
                linked_profile_id=patient["id"],
                password="patient123",
            )
            state["users"][user["id"]] = user
            existing_emails.add(email)
            changed = True

        for doctor in state["doctors"]:
            email = f"{_email_local_part(doctor['name'])}@biosync.local"
            if email in existing_emails:
                continue
            user = self._build_user_record(
                email=email,
                full_name=doctor["name"],
                role="doctor",
                linked_profile_id=doctor["id"],
                password="doctor123",
            )
            state["users"][user["id"]] = user
            existing_emails.add(email)
            changed = True

        return changed

    def _user_public(self, user: dict[str, Any]) -> AuthUser:
        return AuthUser(
            user_id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            linked_profile_id=user["linked_profile_id"],
        )

    def _find_user_by_email_locked(self, email: str) -> Optional[dict[str, Any]]:
        normalized_email = _normalize_email(email)
        for user in self.state["users"].values():
            if _normalize_email(user["email"]) == normalized_email:
                return user
        return None

    def _doctor_public(self, doctor: dict[str, Any]) -> Doctor:
        status = doctor["status"]
        if doctor.get("current_appointment_id") and status != "offline":
            status = "busy"

        return Doctor(
            id=doctor["id"],
            name=doctor["name"],
            specialty=doctor["specialty"],
            status=status,
            rating=doctor["rating"],
            experience=doctor["experience"],
            avatar_url=doctor.get("avatar_url"),
        )

    def _get_doctor_record(self, doctor_id: str) -> dict[str, Any]:
        for doctor in self.state["doctors"]:
            if doctor["id"] == doctor_id:
                return doctor
        raise KeyError("Doctor not found")

    def _get_patient_record(self, patient_id: str) -> dict[str, Any]:
        for patient in self.state["patients"]:
            if patient["id"] == patient_id:
                return patient
        raise KeyError("Patient not found")

    def _get_appointment_record(self, appointment_id: str) -> dict[str, Any]:
        appointment = self.state["appointments"].get(appointment_id)
        if not appointment:
            raise KeyError("Appointment not found")
        return appointment

    def _get_appointment_by_room_locked(self, room_id: str) -> dict[str, Any]:
        for appointment in self.state["appointments"].values():
            if appointment.get("consultation_room_id") == room_id:
                return appointment
        raise KeyError("Consultation room not found")

    def _add_notification_locked(
        self,
        uid: str,
        message: str,
        notif_type: str,
        appointment_id: Optional[str] = None,
    ) -> Notification:
        notification = Notification(
            notification_id=str(uuid.uuid4())[:8],
            recipient_id=uid,
            message=message,
            type=notif_type,
            created_at=_utc_now_iso(),
            appointment_id=appointment_id,
        )
        self.state["notifications"].setdefault(uid, []).append(notification.model_dump())
        return notification

    def _set_doctor_current_appointment(self, doctor_id: str, appointment_id: Optional[str]) -> None:
        doctor = self._get_doctor_record(doctor_id)
        doctor["current_appointment_id"] = appointment_id

    def _recalculate_doctor_rating_locked(self, doctor_id: str) -> None:
        ratings = [
            feedback["rating"]
            for feedback in self.state["feedbacks"].values()
            if feedback["doctor_id"] == doctor_id
        ]
        if not ratings:
            return
        doctor = self._get_doctor_record(doctor_id)
        doctor["rating"] = round(sum(ratings) / len(ratings), 2)

    def list_doctors(self, status: Optional[str] = None) -> list[Doctor]:
        with self.lock:
            doctors = [self._doctor_public(doctor) for doctor in self.state["doctors"]]
            if status:
                doctors = [doctor for doctor in doctors if doctor.status == status]
            return doctors

    def get_doctor(self, doctor_id: str) -> Doctor:
        with self.lock:
            return self._doctor_public(self._get_doctor_record(doctor_id))

    def update_doctor_status(self, doctor_id: str, status: str) -> Doctor:
        with self.lock:
            doctor = self._get_doctor_record(doctor_id)
            if doctor.get("current_appointment_id") and status != "busy":
                raise ValueError("Doctor has an active consultation and must remain busy.")
            doctor["status"] = status
            self._save_state()
            return self._doctor_public(doctor)

    def list_patients(self) -> list[PatientProfile]:
        with self.lock:
            return [PatientProfile(**patient) for patient in self.state["patients"]]

    def get_patient(self, patient_id: str) -> PatientProfile:
        with self.lock:
            return PatientProfile(**self._get_patient_record(patient_id))

    def login_user(self, request: LoginRequest) -> AuthResponse:
        with self.lock:
            user = self._find_user_by_email_locked(request.email)
            if not user or not _verify_password(request.password, user["password_salt"], user["password_hash"]):
                raise ValueError("Invalid email or password.")

            return AuthResponse(
                user=self._user_public(user),
                message="Logged in successfully.",
            )

    def register_user(self, request: RegisterRequest) -> AuthResponse:
        with self.lock:
            normalized_email = _normalize_email(request.email)
            if self._find_user_by_email_locked(normalized_email):
                raise ValueError("An account with this email already exists.")

            full_name = request.full_name.strip()
            if request.role == "patient":
                if request.age is None or not request.condition or not request.condition.strip():
                    raise ValueError("Patient registration requires age and condition.")

                linked_profile_id = f"p{uuid.uuid4().hex[:6]}"
                patient = {
                    "id": linked_profile_id,
                    "name": full_name,
                    "age": request.age,
                    "condition": request.condition.strip(),
                    "last_visit": None,
                    "risk_level": request.risk_level or "Low",
                }
                self.state["patients"].append(patient)
            else:
                if not request.specialty or not request.specialty.strip():
                    raise ValueError("Doctor registration requires a specialty.")

                linked_profile_id = f"d{uuid.uuid4().hex[:6]}"
                doctor = {
                    "id": linked_profile_id,
                    "name": full_name,
                    "specialty": request.specialty.strip(),
                    "status": "available",
                    "rating": 4.5,
                    "experience": request.experience or 0,
                    "avatar_url": None,
                    "current_appointment_id": None,
                }
                self.state["doctors"].append(doctor)

            user = self._build_user_record(
                email=normalized_email,
                full_name=full_name,
                role=request.role,
                linked_profile_id=linked_profile_id,
                password=request.password,
            )
            self.state["users"][user["id"]] = user
            self._save_state()

            return AuthResponse(
                user=self._user_public(user),
                message="Account created successfully.",
            )

    def _validate_appointment_time_locked(
        self,
        doctor_id: str,
        scheduled_time: Optional[str],
        ignore_appointment_id: Optional[str] = None,
    ) -> Optional[str]:
        if not scheduled_time:
            return None

        target = _parse_iso(scheduled_time)
        if target is None:
            return None

        for appointment_id, appointment in self.state["appointments"].items():
            if appointment_id == ignore_appointment_id:
                continue
            if appointment["doctor_id"] != doctor_id:
                continue
            if appointment["status"] not in {"confirmed", "in_progress"}:
                continue

            existing = _parse_iso(appointment.get("scheduled_time"))
            if existing is None:
                continue

            if abs((existing - target).total_seconds()) < 30 * 60:
                raise ValueError("Doctor already has another appointment in that time window.")

        return target.isoformat()

    def create_appointment(self, request: AppointmentRequest) -> Appointment:
        with self.lock:
            patient = self._get_patient_record(request.patient_id)
            doctor_record = self._get_doctor_record(request.doctor_id)
            doctor = self._doctor_public(doctor_record)

            if patient["name"] != request.patient_name:
                raise ValueError("Patient name does not match the selected patient.")
            if doctor.status != "available":
                raise ValueError(f"Doctor is currently {doctor.status}.")

            scheduled_time = self._validate_appointment_time_locked(
                request.doctor_id,
                request.scheduled_time or _utc_now_iso(),
            )
            request_payload = request.model_dump()
            request_payload["scheduled_time"] = scheduled_time

            appointment_id = str(uuid.uuid4())[:8]
            now = _utc_now_iso()
            appointment = Appointment(
                **request_payload,
                appointment_id=appointment_id,
                doctor_name=doctor.name,
                consultation_room_id=f"ROOM-{appointment_id.upper()}",
                created_at=now,
                updated_at=now,
                status="confirmed",
                reminder_sent=False,
            )

            self.state["appointments"][appointment_id] = appointment.model_dump()
            self._add_notification_locked(
                request.patient_id,
                f"Appointment confirmed with {doctor.name} for {scheduled_time}.",
                "appointment",
                appointment_id=appointment_id,
            )
            self._add_notification_locked(
                request.doctor_id,
                f"New {request.consultation_type.lower()} appointment with {request.patient_name} at {scheduled_time}.",
                "appointment",
                appointment_id=appointment_id,
            )
            self._save_state()
            return appointment

    def list_appointments(
        self,
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[Appointment]:
        with self.lock:
            self.generate_due_reminders_locked()

            appointments = [Appointment(**item) for item in self.state["appointments"].values()]
            if role == "patient" and user_id:
                appointments = [appointment for appointment in appointments if appointment.patient_id == user_id]
            elif role == "doctor" and user_id:
                appointments = [appointment for appointment in appointments if appointment.doctor_id == user_id]

            if status:
                wanted = {value.strip() for value in status.split(",") if value.strip()}
                appointments = [appointment for appointment in appointments if appointment.status in wanted]

            appointments.sort(
                key=lambda appointment: (
                    _parse_iso(appointment.scheduled_time or appointment.created_at) or _utc_now(),
                    appointment.created_at,
                )
            )
            return appointments

    def get_appointment(self, appointment_id: str) -> Appointment:
        with self.lock:
            self.generate_due_reminders_locked()
            return Appointment(**self._get_appointment_record(appointment_id))

    def get_consultation_access_context(self, room_id: str, participant_id: str, role: str) -> dict[str, str]:
        normalized_role = role.strip().lower()
        with self.lock:
            appointment = self._get_appointment_by_room_locked(room_id)
            if appointment["status"] not in {"confirmed", "in_progress"}:
                raise ValueError("Consultation room is not currently active.")

            if normalized_role == "patient":
                if appointment["patient_id"] != participant_id:
                    raise ValueError("Patient does not belong to this consultation room.")
                participant_name = appointment["patient_name"]
            elif normalized_role == "doctor":
                if appointment["doctor_id"] != participant_id:
                    raise ValueError("Doctor does not belong to this consultation room.")
                participant_name = appointment["doctor_name"]
            else:
                raise ValueError("Unsupported participant role.")

            return {
                "appointment_id": appointment["appointment_id"],
                "consultation_room_id": appointment["consultation_room_id"],
                "participant_id": participant_id,
                "participant_name": participant_name,
                "role": normalized_role,
                "doctor_id": appointment["doctor_id"],
                "doctor_name": appointment["doctor_name"],
                "patient_id": appointment["patient_id"],
                "patient_name": appointment["patient_name"],
            }

    def update_appointment(self, appointment_id: str, updates: AppointmentUpdateRequest) -> Appointment:
        with self.lock:
            appointment = self._get_appointment_record(appointment_id)
            current_status = appointment["status"]
            if current_status in {"completed", "cancelled"} and updates.status and updates.status != current_status:
                raise ValueError("Completed or cancelled appointments cannot be reopened.")

            payload = updates.model_dump(exclude_unset=True)
            if "scheduled_time" in payload:
                appointment["scheduled_time"] = self._validate_appointment_time_locked(
                    appointment["doctor_id"],
                    payload["scheduled_time"],
                    ignore_appointment_id=appointment_id,
                )
                appointment["reminder_sent"] = False
                self._add_notification_locked(
                    appointment["patient_id"],
                    f"Appointment {appointment_id} was rescheduled to {appointment['scheduled_time']}.",
                    "appointment",
                    appointment_id=appointment_id,
                )
                self._add_notification_locked(
                    appointment["doctor_id"],
                    f"Appointment {appointment_id} was rescheduled to {appointment['scheduled_time']}.",
                    "appointment",
                    appointment_id=appointment_id,
                )

            if "status" in payload:
                new_status = payload["status"]
                appointment["status"] = new_status

                if new_status == "in_progress":
                    self._set_doctor_current_appointment(appointment["doctor_id"], appointment_id)
                    self._add_notification_locked(
                        appointment["patient_id"],
                        f"Consultation for appointment {appointment_id} is now live. Join room {appointment['consultation_room_id']}.",
                        "appointment",
                        appointment_id=appointment_id,
                    )
                elif new_status == "completed":
                    self._set_doctor_current_appointment(appointment["doctor_id"], None)
                    self._add_notification_locked(
                        appointment["patient_id"],
                        f"Appointment {appointment_id} is completed. Please submit your feedback.",
                        "feedback",
                        appointment_id=appointment_id,
                    )
                elif new_status == "cancelled":
                    self._set_doctor_current_appointment(appointment["doctor_id"], None)
                    self._add_notification_locked(
                        appointment["patient_id"],
                        f"Appointment {appointment_id} has been cancelled.",
                        "appointment",
                        appointment_id=appointment_id,
                    )
                    self._add_notification_locked(
                        appointment["doctor_id"],
                        f"Appointment {appointment_id} has been cancelled.",
                        "appointment",
                        appointment_id=appointment_id,
                    )

            appointment["updated_at"] = _utc_now_iso()
            self._save_state()
            return Appointment(**appointment)

    def get_notifications(self, uid: str, unread_only: bool = False) -> list[Notification]:
        with self.lock:
            self.generate_due_reminders_locked()
            items = [Notification(**item) for item in self.state["notifications"].get(uid, [])]
            if unread_only:
                items = [item for item in items if not item.read]
            items.sort(key=lambda item: item.created_at, reverse=True)
            return items

    def mark_notification_read(self, uid: str, notification_id: str) -> None:
        with self.lock:
            for item in self.state["notifications"].get(uid, []):
                if item["notification_id"] == notification_id:
                    item["read"] = True
                    self._save_state()
                    return
            raise KeyError("Notification not found")

    def generate_due_reminders_locked(self, lead_minutes: int = 30) -> int:
        now = _utc_now()
        generated = 0

        for appointment in self.state["appointments"].values():
            if appointment["status"] != "confirmed" or appointment.get("reminder_sent"):
                continue

            scheduled_at = _parse_iso(appointment.get("scheduled_time"))
            if scheduled_at is None:
                continue

            delta = scheduled_at - now
            if timedelta(0) <= delta <= timedelta(minutes=lead_minutes):
                message = (
                    f"Reminder: appointment {appointment['appointment_id']} with "
                    f"{appointment['doctor_name']} starts at {appointment['scheduled_time']}."
                )
                self._add_notification_locked(
                    appointment["patient_id"],
                    message,
                    "reminder",
                    appointment_id=appointment["appointment_id"],
                )
                self._add_notification_locked(
                    appointment["doctor_id"],
                    f"Reminder: consultation with {appointment['patient_name']} starts at {appointment['scheduled_time']}.",
                    "reminder",
                    appointment_id=appointment["appointment_id"],
                )
                appointment["reminder_sent"] = True
                generated += 1

        if generated:
            self._save_state()
        return generated

    def generate_due_reminders(self, lead_minutes: int = 30) -> int:
        with self.lock:
            return self.generate_due_reminders_locked(lead_minutes=lead_minutes)

    def submit_feedback(self, request: FeedbackRequest) -> Feedback:
        with self.lock:
            appointment = self._get_appointment_record(request.appointment_id)
            if appointment["patient_id"] != request.patient_id or appointment["doctor_id"] != request.doctor_id:
                raise ValueError("Feedback does not match the appointment participants.")
            if appointment["status"] != "completed":
                raise ValueError("Feedback can only be submitted for completed appointments.")

            for feedback in self.state["feedbacks"].values():
                if feedback["appointment_id"] == request.appointment_id:
                    raise ValueError("Feedback was already submitted for this appointment.")

            patient = self._get_patient_record(request.patient_id)
            doctor = self._get_doctor_record(request.doctor_id)
            feedback = Feedback(
                **request.model_dump(),
                feedback_id=str(uuid.uuid4())[:8],
                patient_name=patient["name"],
                doctor_name=doctor["name"],
                created_at=_utc_now_iso(),
            )

            self.state["feedbacks"][feedback.feedback_id] = feedback.model_dump()
            self._recalculate_doctor_rating_locked(request.doctor_id)
            self._add_notification_locked(
                request.doctor_id,
                f"New feedback received from {patient['name']} for appointment {request.appointment_id}.",
                "feedback",
                appointment_id=request.appointment_id,
            )
            self._save_state()
            return feedback

    def list_feedback(
        self,
        doctor_id: Optional[str] = None,
        patient_id: Optional[str] = None,
    ) -> list[Feedback]:
        with self.lock:
            feedbacks = [Feedback(**item) for item in self.state["feedbacks"].values()]
            if doctor_id:
                feedbacks = [feedback for feedback in feedbacks if feedback.doctor_id == doctor_id]
            if patient_id:
                feedbacks = [feedback for feedback in feedbacks if feedback.patient_id == patient_id]
            feedbacks.sort(key=lambda feedback: feedback.created_at, reverse=True)
            return feedbacks

    def feedback_summary(
        self,
        doctor_id: Optional[str] = None,
        patient_id: Optional[str] = None,
    ) -> FeedbackSummary:
        feedbacks = self.list_feedback(doctor_id=doctor_id, patient_id=patient_id)
        total = len(feedbacks)
        if total == 0:
            return FeedbackSummary(
                total_feedback=0,
                avg_rating=0.0,
                avg_communication=0.0,
                avg_wait_time=0.0,
                recommend_percent=0.0,
                low_ratings=0,
            )

        low_ratings = len([feedback for feedback in feedbacks if feedback.rating <= 2])
        recommend_count = len([feedback for feedback in feedbacks if feedback.recommend])
        return FeedbackSummary(
            total_feedback=total,
            avg_rating=round(sum(feedback.rating for feedback in feedbacks) / total, 2),
            avg_communication=round(sum(feedback.communication for feedback in feedbacks) / total, 2),
            avg_wait_time=round(sum(feedback.wait_time for feedback in feedbacks) / total, 2),
            recommend_percent=round((recommend_count / total) * 100, 1),
            low_ratings=low_ratings,
        )


store = ClinicStore()

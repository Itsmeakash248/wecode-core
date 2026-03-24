"""
Frontend HTTP client for the BioSync backend.
"""
from __future__ import annotations

import os
from typing import Any, Optional

import httpx


API_BASE_URL = os.getenv("BIOSYNC_API_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("BIOSYNC_API_TIMEOUT", "8"))
EXPECTED_BACKEND_SERVICE = "BioSync Tele-Rescue Backend"
REQUIRED_AUTH_PATHS = {"/auth/login", "/auth/register"}


class BackendUnavailable(RuntimeError):
    """Raised when the backend cannot be reached."""


class ApiError(RuntimeError):
    """Raised when the backend returns an error response."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


def _supports_auth_backend() -> bool:
    health_url = f"{API_BASE_URL}/health"
    openapi_url = f"{API_BASE_URL}/openapi.json"
    timeout = min(REQUEST_TIMEOUT, 3.0)

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(health_url)
    except httpx.RequestError:
        return False

    if response.is_error:
        return False

    try:
        payload = response.json()
    except ValueError:
        return False

    if payload.get("service") != EXPECTED_BACKEND_SERVICE:
        return False

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(openapi_url)
    except httpx.RequestError:
        return False

    if response.is_error:
        return False

    try:
        payload = response.json()
    except ValueError:
        return False

    available_paths = set(payload.get("paths", {}))
    return REQUIRED_AUTH_PATHS.issubset(available_paths)


def _request(
    method: str,
    path: str,
    *,
    params: Optional[dict[str, Any]] = None,
    json: Optional[dict[str, Any]] = None,
) -> Any:
    url = f"{API_BASE_URL}{path}"
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.request(method, url, params=params, json=json)
    except httpx.RequestError as exc:
        raise BackendUnavailable(
            f"Backend is unavailable at {API_BASE_URL}. Start the FastAPI server first."
        ) from exc

    if response.is_error:
        if response.status_code == 404 and path.startswith("/auth/"):
            if not _supports_auth_backend():
                raise BackendUnavailable(
                    f"Incompatible or stale backend detected at {API_BASE_URL}. "
                    "Stop anything using port 8000, then start this project with `bash start.sh` "
                    "or `python run_dashboard.py`."
                )
            raise ApiError(
                f"BioSync backend is running at {API_BASE_URL}, but the auth route `{path}` is missing. "
                "Restart the backend from this repository.",
                response.status_code,
            )

        message = response.text
        try:
            payload = response.json()
            message = payload.get("detail", message)
        except ValueError:
            pass
        raise ApiError(str(message), response.status_code)

    if response.status_code == 204 or not response.content:
        return None
    return response.json()


def health() -> dict[str, Any]:
    return _request("GET", "/health")


def login(payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/auth/login", json=payload)


def register(payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/auth/register", json=payload)


def list_patients() -> list[dict[str, Any]]:
    return _request("GET", "/patients")


def list_doctors(status: Optional[str] = None) -> list[dict[str, Any]]:
    params = {"status": status} if status else None
    return _request("GET", "/doctors", params=params)


def update_doctor_status(doctor_id: str, status: str) -> dict[str, Any]:
    return _request("PATCH", f"/doctors/{doctor_id}/status", json={"status": status})


def list_appointments(
    *,
    user_id: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
) -> list[dict[str, Any]]:
    params = {}
    if user_id:
        params["user_id"] = user_id
    if role:
        params["role"] = role
    if status:
        params["status"] = status
    return _request("GET", "/appointments", params=params or None)


def get_appointment(appointment_id: str) -> dict[str, Any]:
    return _request("GET", f"/appointments/{appointment_id}")


def book_appointment(payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/appointments", json=payload)


def update_appointment(appointment_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return _request("PATCH", f"/appointments/{appointment_id}", json=payload)


def list_notifications(uid: str, unread_only: bool = False) -> list[dict[str, Any]]:
    params = {"unread_only": unread_only} if unread_only else None
    return _request("GET", f"/notifications/{uid}", params=params)


def mark_notification_read(uid: str, notification_id: str) -> dict[str, Any]:
    return _request("PATCH", f"/notifications/{uid}/{notification_id}/read")


def process_reminders() -> dict[str, Any]:
    return _request("POST", "/notifications/process-reminders")


def submit_feedback(payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/feedback", json=payload)


def list_feedback(
    *,
    doctor_id: Optional[str] = None,
    patient_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    params = {}
    if doctor_id:
        params["doctor_id"] = doctor_id
    if patient_id:
        params["patient_id"] = patient_id
    return _request("GET", "/feedback", params=params or None)


def feedback_summary(
    *,
    doctor_id: Optional[str] = None,
    patient_id: Optional[str] = None,
) -> dict[str, Any]:
    params = {}
    if doctor_id:
        params["doctor_id"] = doctor_id
    if patient_id:
        params["patient_id"] = patient_id
    return _request("GET", "/feedback/summary", params=params or None)

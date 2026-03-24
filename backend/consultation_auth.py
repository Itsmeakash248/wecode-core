"""
Signed access tokens for consultation rooms.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any


DEFAULT_TOKEN_TTL_SECONDS = 60 * 60 * 4
SECRET_ENV_VAR = "BIOSYNC_CONSULTATION_SECRET"
DEFAULT_SECRET = "biosync-dev-consultation-secret"


def _secret() -> bytes:
    return os.getenv(SECRET_ENV_VAR, DEFAULT_SECRET).encode("utf-8")


def _encode_payload(payload: dict[str, Any]) -> str:
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(_secret(), payload_bytes, hashlib.sha256).hexdigest()
    encoded_payload = base64.urlsafe_b64encode(payload_bytes).decode("ascii").rstrip("=")
    return f"{encoded_payload}.{signature}"


def _decode_payload(token: str) -> dict[str, Any] | None:
    try:
        encoded_payload, signature = token.split(".", 1)
        padded_payload = encoded_payload + "=" * (-len(encoded_payload) % 4)
        payload_bytes = base64.urlsafe_b64decode(padded_payload.encode("ascii"))
        expected_signature = hmac.new(_secret(), payload_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return None
        return json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None


def issue_consultation_token(
    room_id: str,
    participant_id: str,
    role: str,
    *,
    ttl_seconds: int = DEFAULT_TOKEN_TTL_SECONDS,
) -> str:
    payload = {
        "room_id": room_id,
        "participant_id": participant_id,
        "role": role.strip().lower(),
        "exp": int(time.time()) + ttl_seconds,
    }
    return _encode_payload(payload)


def verify_consultation_token(token: str, room_id: str, participant_id: str, role: str) -> bool:
    payload = _decode_payload(token)
    if payload is None:
        return False

    expected_role = role.strip().lower()
    if payload.get("room_id") != room_id:
        return False
    if payload.get("participant_id") != participant_id:
        return False
    if payload.get("role") != expected_role:
        return False
    if int(payload.get("exp", 0)) < int(time.time()):
        return False
    return True

"""
Ollama LLM integration — generates doctor triage briefs on anomaly events.
Falls back to a hardcoded string if Ollama is unavailable (demo resilience).
"""
import os
import httpx
from dotenv import load_dotenv
from backend.models import VitalsPayload

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3")

SYSTEM_PROMPT = (
    "You are a medical triage AI. Given an anomaly alert with patient vitals, "
    "output a 2-sentence triage briefing for an incoming teleconsulting emergency doctor. "
    "Include the suspected issue and the immediate recommended intervention."
)

FALLBACK_BRIEF = (
    "CRITICAL ALERT: Patient vitals indicate emergency — severely low SpO2 or dangerous heart rate. "
    "Immediate teleconsultation required; prepare for potential cardiac or respiratory intervention."
)


def get_triage_brief(vitals: VitalsPayload, anomaly_score: float) -> str:
    """
    Call Ollama to generate a 2-sentence doctor triage brief.
    Returns a hardcoded fallback string if Ollama is unavailable.
    """
    user_message = (
        f"ANOMALY ALERT — Anomaly Score: {anomaly_score}\n"
        f"Heart Rate: {vitals.heart_rate} bpm\n"
        f"SpO2: {vitals.spo2}%\n"
        f"Accelerometer: x={vitals.accelerometer_x}, y={vitals.accelerometer_y}, z={vitals.accelerometer_z}\n"
        f"Timestamp: {vitals.timestamp}\n\n"
        "Generate a 2-sentence doctor triage brief."
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": user_message,
        "system": SYSTEM_PROMPT,
        "stream": False,
    }

    try:
        with httpx.Client(timeout=8.0) as client:
            response = client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", FALLBACK_BRIEF).strip()
    except Exception:
        return FALLBACK_BRIEF

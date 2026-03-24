"""
Google Gemini LLM integration — generates doctor triage briefs on anomaly events.
Falls back to a hardcoded string if the API key is missing or the call fails.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from backend.models import VitalsPayload

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

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
    Call Google Gemini to generate a 2-sentence doctor triage brief.
    Returns a hardcoded fallback string if the API key is missing or the call fails.
    """
    if not GEMINI_API_KEY:
        return FALLBACK_BRIEF

    user_message = (
        f"{SYSTEM_PROMPT}\n\n"
        f"ANOMALY ALERT — Anomaly Score: {anomaly_score}\n"
        f"Heart Rate: {vitals.heart_rate} bpm\n"
        f"SpO2: {vitals.spo2}%\n"
        f"Accelerometer: x={vitals.accelerometer_x}, y={vitals.accelerometer_y}, z={vitals.accelerometer_z}\n"
        f"Timestamp: {vitals.timestamp}\n\n"
        "Generate a 2-sentence doctor triage brief."
    )

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(user_message)
        return response.text.strip() or FALLBACK_BRIEF
    except Exception:
        return FALLBACK_BRIEF

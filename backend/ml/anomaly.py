"""
Isolation Forest anomaly detector for patient vitals.
Trains on synthetic 'normal' baseline at import time — no external data needed.
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from backend.models import VitalsPayload


# ─── Baseline Training ────────────────────────────────────────────────────────

def _build_normal_baseline(n: int = 500) -> np.ndarray:
    """Generate synthetic normal vitals: HR 60-100, SpO2 95-100, mild accel."""
    rng = np.random.default_rng(42)
    hr   = rng.uniform(60, 100, n)
    spo2 = rng.uniform(95, 100, n)
    ax   = rng.uniform(-0.2, 0.2, n)
    ay   = rng.uniform(-0.2, 0.2, n)
    az   = rng.uniform(9.6, 10.0, n)     # normal gravity along Z
    return np.column_stack([hr, spo2, ax, ay, az])


_model = IsolationForest(contamination=0.05, random_state=42)
_model.fit(_build_normal_baseline())


# ─── Public API ───────────────────────────────────────────────────────────────

def detect(vitals: VitalsPayload) -> tuple[bool, float]:
    """
    Returns (is_anomaly, raw_score).
    Score < 0 means the IF model considers it anomalous.
    We also hard-flag critical clinical thresholds regardless of IF score.
    """
    features = np.array([[
        vitals.heart_rate,
        vitals.spo2,
        vitals.accelerometer_x,
        vitals.accelerometer_y,
        vitals.accelerometer_z,
    ]])

    score: float = float(_model.score_samples(features)[0])
    model_flags = _model.predict(features)[0] == -1   # -1 = anomaly

    # Clinical hard-threshold override
    clinical_flag = vitals.is_critical()

    is_anomaly = model_flags or clinical_flag
    return is_anomaly, round(score, 4)

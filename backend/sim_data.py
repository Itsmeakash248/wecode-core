"""
sim_data.py — Simulated Patient Vitals Generator

Simulates an ESP32 wearable streaming data to the BioSync backend.

Phase 1 (first 10 readings): Normal vitals
Phase 2 (remaining readings): CRITICAL vitals — SpO2 drop + elevated HR + fall acceleration

Usage:
    python -m backend.sim_data
"""

import time
import random
import httpx
from datetime import datetime, timezone

API_URL = "http://127.0.0.1:8000/vitals"
INTERVAL = 1.0   # seconds between readings
NORMAL_READINGS = 10


def normal_vitals() -> dict:
    return {
        "heart_rate":      round(random.uniform(65, 90), 1),
        "spo2":            round(random.uniform(96, 99), 1),
        "accelerometer_x": round(random.uniform(-0.1, 0.1), 3),
        "accelerometer_y": round(random.uniform(-0.1, 0.1), 3),
        "accelerometer_z": round(random.uniform(9.7, 9.9), 3),
        "timestamp":       datetime.now(timezone.utc).isoformat(),
    }


def critical_vitals() -> dict:
    """Simulates cardiac event: low SpO2, high HR, and a fall (Z-axis spike)."""
    return {
        "heart_rate":      round(random.uniform(145, 160), 1),
        "spo2":            round(random.uniform(83, 89), 1),
        "accelerometer_x": round(random.uniform(1.8, 3.0), 3),
        "accelerometer_y": round(random.uniform(-3.5, -2.0), 3),
        "accelerometer_z": round(random.uniform(0.5, 1.5), 3),   # fall = lost gravity
        "timestamp":       datetime.now(timezone.utc).isoformat(),
    }


def main():
    print("🚀 BioSync Vitals Simulator starting...")
    print(f"   Target: {API_URL}")
    print(f"   Phase 1: {NORMAL_READINGS} normal readings")
    print(f"   Phase 2: Critical vitals until stopped (Ctrl+C)\n")

    reading = 0
    with httpx.Client(timeout=5.0) as client:
        while True:
            reading += 1
            phase = "NORMAL  " if reading <= NORMAL_READINGS else "CRITICAL"
            data  = normal_vitals() if reading <= NORMAL_READINGS else critical_vitals()

            try:
                resp = client.post(API_URL, json=data)
                resp.raise_for_status()
                result = resp.json()

                anomaly_flag = "🚨 ANOMALY" if result["is_anomaly"] else "✅ Normal"
                brief        = result.get("triage_brief", "")
                score        = result.get("anomaly_score", "n/a")

                print(f"[{reading:03d}] [{phase}] HR={data['heart_rate']} SpO2={data['spo2']}% "
                      f"| Score={score} | {anomaly_flag}")

                if result["is_anomaly"] and brief:
                    print(f"         📋 Triage: {brief[:120]}...")

            except httpx.ConnectError:
                print(f"[{reading:03d}] ❌ Cannot connect to {API_URL} — is the server running?")
            except Exception as e:
                print(f"[{reading:03d}] ❌ Error: {e}")

            time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Simulation stopped.")

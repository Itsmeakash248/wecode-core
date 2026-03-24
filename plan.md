# 🚨 BIOSYNC AI — EMERGENCY PIVOT BATTLE PLAN

> **HackArena 2K26 · Healthcare Track · Team: We Code Together**
> **Problem Statement:** Healthcare PS 1 — Doctor Availability & Teleconsultation Platform
> **Current Time:** 11:00 AM · **Evaluation Begins:** 3:00 PM · **Time Budget:** 4 hours

---

## 1 · The Strategic Pivot: "BioSync Tele-Rescue"

| | |
|---|---|
| **Threat** | Our original "offline bystander CPR" idea does not align with any official HackArena problem statement — we risk disqualification. |
| **Pivot Target** | Healthcare PS 1 — Doctor Availability & Teleconsultation Platform |
| **Core Insight** | Every existing teleconsultation platform assumes the patient is conscious and able to book a call. That assumption fails catastrophically during cardiac events, falls, and seizures. |

### The Elevator Pitch

> *"When our edge-AI wearable detects a critical drop in vitals — cardiac arrest, a dangerous fall — it bypasses the booking process and instantly auto-dials the nearest available emergency doctor via WebRTC, streaming live patient vitals and an AI-generated triage brief directly to the doctor's screen."*

---

## 2 · Role Delegation (11:00 AM →)

### 👨‍💻 Akash — Hardware · ML Core · Backend

| Window | Deliverable | Exit Condition |
|---|---|---|
| 11:00 – 12:30 | **AI & Data Pipeline** — Finish FastAPI ingestion + Scikit-Learn Isolation Forest. Wire `sim_data.py` to trigger anomaly threshold cleanly. | Anomaly detection fires reliably on simulated vitals. |
| 12:30 – 13:30 | **Backend WebSocket** — Expose a WS endpoint that pushes live data to the remote "Doctor's Dashboard" (not just a local screen). | Doctor dashboard receives real-time data over WebSocket. |
| 13:30 – 14:30 | **Integration** — Connect the anomaly trigger → Shweta's updated UI. End-to-end run. | Full pipeline works without manual intervention. |

### 👩‍💻 Shweta — LLM · UI/UX · Narrative Pivot

| Window | Deliverable | Exit Condition |
|---|---|---|
| 11:00 – 12:00 | **Ollama Prompt Update** — Rewrite the LLM system prompt so the AI now briefs a *doctor*, not a bystander. | Prompt produces a clean 2-sentence doctor triage brief. |
| 12:00 – 14:00 | **UI Overhaul (Streamlit)** — Build two views. | Both views render correctly with mock data. |
| 14:00 – 14:30 | **Polish** — Ensure UI prominently labels itself "Teleconsultation Portal". | Judges' rubric keywords visible on every screen. |

#### New LLM System Prompt

```
SYSTEM: You are a medical triage AI. Given an anomaly alert, output a 2-sentence
triage briefing for an incoming teleconsulting emergency doctor. Include suspected
issue and immediate recommended intervention.
```

#### Streamlit UI Spec

| View | Contents |
|---|---|
| **Patient View** | Normal vitals monitoring dashboard. |
| **Doctor Platform** | Sidebar: "Available Doctors (Online)" list. Main area: live vitals feed. |
| **SOS Trigger** | Screen turns red → "CRITICAL: Auto-Dialing Available Doctor…" → Mock WebRTC video placeholder (static image or webcam iframe). |

---

## 3 · Countdown Timeline

| Time | Phase | Action / Exit Condition |
|:---|:---|:---|
| **11:00 – 12:30** | Core Backend | FastAPI receiving data · Isolation Forest triggering anomalies · Ollama outputting doctor briefs. |
| **12:30 – 14:00** | UI/UX Pivot | Streamlit dashboard built. Must include "Available Doctors" list + WebRTC video mock. |
| **14:00 – 14:45** | Integration | End-to-end: ESP32/Sim → Anomaly → Auto-dial Doctor UI → LLM text + Fake video feed. |
| **14:45 – 15:00** | Demo Prep | **STOP CODING.** Clean desk · open all tabs · prepare for judges. |
| **15:00 – 16:30** | Evaluation | Pitch to judges (see script below). |
| **17:00 →** | Code Freeze | Prep codebase for Cross-Fire Debugging Hunt. Add clear comments to `sim_data.py`. |

---

## 4 · The 3-Minute Pitch Script

### 🎙️ Act 1 — The Hook (0:00 – 0:30)

> "We chose the Teleconsultation Platform problem statement. But we found a fatal flaw in modern telehealth: **it assumes the patient is conscious and able to book a call.** What happens during a sudden cardiac event or a severe fall? They can't navigate a UI."

### 🎙️ Act 2 — The Solution (0:30 – 1:15)

> "Meet **BioSync Tele-Rescue** — an autonomous edge-AI teleconsultation trigger. Right now, vitals are streaming normally from this $6 ESP32 wearable. The platform shows nearby doctors are available, but idle."

### 🎙️ Act 3 — The "Aha!" Moment (1:15 – 2:00)

> "Watch what happens when I simulate a critical SpO2 drop and a fall. *(trigger anomaly)* Our local Isolation Forest model detects the crash instantly. Instead of just ringing an alarm, it **bypasses the booking system and automatically initiates a WebRTC emergency teleconsultation** with the nearest available doctor. The doctor receives live vitals and an AI-generated triage brief from our local Ollama model."

### 🎙️ Act 4 — Tech Stack & Close (2:00 – 2:30)

> "FastAPI, Streamlit, local LLMs, deterministic ML. We didn't build a doctor booking app — we built an **autonomous lifeline** that uses teleconsultation to reclaim the golden hour. Thank you."

---

## 5 · Fallback Ladder

> If things break at 2:50 PM — **don't panic, degrade gracefully:**

| Priority | Failure | Fallback |
|:---:|---|---|
| 1 | Hardware fails | Switch to `sim_data.py`. *"We're simulating the wearable feed to demonstrate the software pipeline."* |
| 2 | LLM too slow | Hardcode the triage string. Judges won't know during a 3-min pitch. |
| 3 | Streamlit crashes | Show FastAPI backend logs detecting the anomaly + triggering "Call Doctor" in the terminal. **The logic is what matters.** |

---

> **🔥 STAY CALM. A working prototype with a great story beats broken, complex code. Let's win this.**
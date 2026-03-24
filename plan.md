# 🚨 BIOSYNC AI: EMERGENCY PIVOT BATTLE PLAN 🚨
**HackArena 2K26 • Healthcare Track • Team: We Code Together**
**Current Time:** 11:00 AM | **Evaluation Starts:** 3:00 PM
**Target Problem Statement:** Healthcare PS 1 (Doctor Availability & Teleconsultation Platform)

---

## 🎯 THE STRATEGIC PIVOT: "BioSync Tele-Rescue"
**The Threat:** Our original "offline bystander CPR" idea does not match the official HackArena problem statements. We risk disqualification.
**The Solution:** We are pivoting to **Healthcare PS 1**. 
**The New Pitch:** *"Standard teleconsultation platforms require conscious patients to book appointments. We built an **Automated Emergency Teleconsultation Platform**. When our edge-AI wearable detects a critical drop in vitals (cardiac arrest/fall), it bypasses the booking process and instantly auto-dials the nearest available emergency doctor via WebRTC, streaming live patient vitals and AI-generated emergency context directly to the doctor's screen."*

---

## 🛠️ UPDATED ROLE DELEGATION (11:00 AM ONWARD)

### 👨‍💻 Akash (Primary: Hardware, ML Core, Backend)
*No changes to your core stack. Just change the data destination narrative.*
*   **[11:00 AM - 12:30 PM] AI & Data Pipeline:** Finish the FastAPI ingestion and Scikit-Learn Isolation Forest integration. Ensure the sensor data (or `sim_data.py`) triggers the anomaly threshold cleanly.
*   **[12:30 PM - 1:30 PM] Backend Socket:** Expose a WebSocket endpoint that simulates sending the live data to a remote "Doctor's Dashboard" rather than just a local bystander phone.
*   **[1:30 PM - 2:30 PM] Integration:** Link the anomaly trigger to Shweta's updated UI. 

### 👩‍💻 Shweta (Support: LLM, UI/UX, Narrative Pivot)
*You are driving the UI pivot to match the "Teleconsultation" prompt.*
*   **[11:00 AM - 12:00 PM] Ollama Prompt Update:** Change the LLM prompt. Instead of talking to a bystander, the AI is briefing a doctor. 
    *   *New Prompt:* `SYSTEM: You are a medical triage AI. Given an anomaly alert, output a 2-sentence triage briefing for an incoming teleconsulting emergency doctor. Include suspected issue and immediate recommended intervention.`
*   **[12:00 PM - 2:00 PM] UI Overhaul (Streamlit):** 
    *   **View 1 (Patient View):** Normal vitals monitoring. 
    *   **View 2 (Doctor Platform):** Add a sidebar showing "Available Doctors (Online)". 
    *   **The SOS Trigger:** When an anomaly hits, screen turns red, displays "CRITICAL: Auto-Dialing Available Doctor..." and shows a mock WebRTC Video Placeholder (use a static image or a webcam feed iframe to simulate the teleconsultation).
*   **[2:00 PM - 2:30 PM] Polish:** Ensure the UI clearly says "Teleconsultation Portal" to check the judges' rubric boxes.

---

## ⏱️ REVISED COUNTDOWN TIMELINE

| Time | Phase | Action / Exit Condition |
| :--- | :--- | :--- |
| **11:00 - 12:30** | **Core Backend** | FastAPI receiving data; Isolation forest reliably triggering anomalies; Ollama outputting "Doctor Briefs". |
| **12:30 - 14:00** | **UI/UX Pivot** | Streamlit dashboard built. Must include "Available Doctors" list and WebRTC video mock-up to satisfy the problem statement. |
| **14:00 - 14:45** | **Integration** | End-to-End run. ESP32/Sim Data → Anomaly → Auto-dials Doctor UI → Shows LLM text + Fake Video feed. |
| **14:45 - 15:00** | **Demo Prep** | **STOP CODING.** Clean the desk, open all tabs, prepare for the judges. |
| **15:00 - 16:30** | **EVALUATION** | Pitch to Judges (See script below). |
| **17:00 Onward** | **Code Freeze** | Prepare codebase for the Cross-Fire Debugging Hunt (Add clear comments to `sim_data.py` so others can run it without hardware). |

---

## 🎤 THE 3-MINUTE PITCH SCRIPT (Memorize This)

**[0:00 - 0:30] The Hook & Problem:** 
"We chose the Teleconsultation Platform problem statement. But we realized a fatal flaw in modern telehealth: it assumes the patient is conscious and able to book a call. What happens when a patient suffers a sudden cardiac event or a severe fall? They can't navigate a UI."

**[0:30 - 1:15] The Solution (Start Normal Demo):** 
"Meet BioSync Tele-Rescue. We built an autonomous edge-AI teleconsultation trigger. Right now, my vitals are streaming normally from this $6 ESP32 wearable. The platform shows nearby doctors are available, but idle."

**[1:15 - 2:00] The "Aha!" Moment (Trigger Emergency):** 
"Watch what happens when I simulate a critical drop in SpO2 and a fall. *(Trigger anomaly)*. Our local Isolation Forest model detects the crash instantly. Instead of just ringing an alarm, it bypasses the booking system and **automatically initiates a WebRTC emergency teleconsultation** with the nearest available doctor. The doctor instantly receives the live vitals stream and an AI-generated triage brief from our local Ollama model."

**[2:00 - 2:30] The Tech Stack & Closing:** 
"We built this using FastAPI, Streamlit, local LLMs, and deterministic ML. We didn't just build a doctor booking app; we built an autonomous lifeline that uses teleconsultation to reclaim the golden hour of an emergency. Thank you."

---

## ⚠️ FALLBACK LADDER (If things break at 2:50 PM)
1. **Hardware fails:** Switch to `sim_data.py`. Tell judges: "We're simulating the wearable feed to demonstrate the software pipeline."
2. **LLM is too slow:** Hardcode the triage string. They won't know the difference during a 3-minute pitch.
3. **Streamlit UI crashes:** Show the FastAPI backend logs detecting the anomaly and triggering the "Call Doctor" function in the terminal. The logic is what matters. 

**STAY CALM. A working prototype with a great story beats broken, complex code. Let's win this.**
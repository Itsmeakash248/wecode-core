# Wecode Core

## BioSync Tele-Rescue

An autonomous edge-AI teleconsultation platform that revolutionizes emergency healthcare by automatically connecting patients to doctors during critical moments.

### Features

- **🏠 Landing Page**: Professional introduction to the platform with key features and navigation
- **👤 Patient Dashboard**: Real-time vitals monitoring with emergency SOS trigger
- **👨‍⚕️ Doctor Platform**: Modern, clean healthcare telemedicine dashboard with comprehensive analytics

### Doctor Dashboard Features

#### 🎨 Modern UI Design
- **Minimal & Professional**: Clean white, blue, and soft green color palette
- **Futuristic Elements**: Soft shadows, rounded cards, smooth animations
- **Medical Theme**: Healthcare-focused design with appropriate icons and colors

#### 📊 Dashboard Sections
- **Overview Cards**: Total consultations, active patients, emergency cases, today's appointments
- **Analytics Charts**: Line chart for consultation trends, pie chart for patient categories
- **Recent Activity**: List of recent consultations with status badges
- **Upcoming Appointments**: Doctor schedule with time slots and join call buttons
- **Emergency Alert Panel**: Highlight urgent cases with red accent and pulse animation
- **Patient Insights**: Health stats cards with medical icons

#### 🧭 Navigation
- **Sidebar Navigation**: Dashboard, Appointments, Patients, Reports, Emergency sections
- **Emergency Section**: Live vitals feed and AI triage briefs for critical cases
- **🤖 AI-Powered Detection**: Edge-AI wearables detect critical vitals anomalies
- **🚨 Auto-Dial Emergency**: Automatically initiates teleconsultation when anomalies are detected
- **📹 Live Video & Vitals**: Streams live patient vitals and video feed to available doctors

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### How to Run

#### **Option 1: One-Click Launcher (Recommended)**
```bash
# Windows
run_dashboard.bat

# Linux/Mac
./run_dashboard.sh

# Cross-platform
python run_dashboard.py
```

#### **Option 2: Manual Run**
```bash
# Run the application
streamlit run app.py
```

#### **Option 3: Custom Configuration**
```bash
# Run on specific port
streamlit run app.py --server.port 8502 --server.headless true
```

### Quick Start

1. **Download/Clone** the project
2. **Double-click** `run_dashboard.bat` (Windows) or run `python run_dashboard.py`
3. **Open** http://localhost:8501 in your browser
4. **Navigate** through the dashboard sections

### Usage

- **Home**: View the landing page with platform overview
- **Patient Dashboard**: Monitor vitals and simulate emergency scenarios
- **Doctor Platform**: Access the comprehensive telemedicine dashboard

### Tech Stack

- **Frontend**: Streamlit with custom CSS
- **Data Visualization**: Plotly charts, Streamlit native charts
- **AI/ML**: Edge-AI for anomaly detection (planned)
- **Communication**: WebRTC for video consultations (planned)
- **Backend**: FastAPI (planned)

### HackArena 2K26

Developed for HackArena 2K26 Healthcare Track - Doctor Availability & Teleconsultation Platform

### Dashboard Screenshots

The dashboard features a modern, responsive design optimized for both desktop and mobile viewing, with:
- High-fidelity UI similar to top healthcare applications
- Clean spacing and professional typography
- Intuitive icon-based navigation
- Real-time data visualization
- Emergency alert system with visual prominence
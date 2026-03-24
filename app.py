import streamlit as st
import time
import random
import pandas as pd
import numpy as np

# Mock data for vitals
def get_mock_vitals():
    return {
        'Heart Rate': random.randint(60, 100),
        'SpO2': random.randint(95, 100),
        'Temperature': round(random.uniform(36.5, 37.5), 1),
        'Blood Pressure': f"{random.randint(110, 130)}/{random.randint(70, 90)}"
    }

# Mock doctors
doctors = [
    {"name": "Dr. Smith", "specialty": "Cardiology", "status": "Available"},
    {"name": "Dr. Johnson", "specialty": "Emergency", "status": "Available"},
    {"name": "Dr. Lee", "specialty": "Neurology", "status": "Busy"},
]

# Mock data for dashboard
def get_dashboard_data():
    return {
        'total_consultations': 1247,
        'active_patients': 89,
        'emergency_cases': 12,
        'today_appointments': 8
    }

def get_recent_activity():
    activities = [
        {"patient": "John Doe", "time": "10:30 AM", "status": "Completed", "type": "Regular Checkup"},
        {"patient": "Sarah Wilson", "time": "09:45 AM", "status": "In Progress", "type": "Emergency"},
        {"patient": "Mike Johnson", "time": "09:15 AM", "status": "Completed", "type": "Follow-up"},
        {"patient": "Emma Davis", "time": "08:30 AM", "status": "Completed", "type": "Consultation"},
        {"patient": "Robert Brown", "time": "08:00 AM", "status": "Completed", "type": "Regular Checkup"},
    ]
    return activities

def get_upcoming_appointments():
    appointments = [
        {"time": "11:00 AM", "patient": "Alice Cooper", "type": "Cardiology Review"},
        {"time": "11:30 AM", "patient": "Bob Wilson", "type": "Follow-up"},
        {"time": "02:00 PM", "patient": "Carol Smith", "type": "Consultation"},
        {"time": "03:30 PM", "patient": "David Johnson", "type": "Emergency Review"},
    ]
    return appointments

st.set_page_config(
    page_title="BioSync Tele-Rescue - Doctor Dashboard",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for navigation
view = st.sidebar.selectbox("Navigation", ["🏠 Home", "👤 Patient Dashboard", "👨‍⚕️ Doctor Platform"])

if view == "🏠 Home":
    # Landing Page
    st.markdown("""
    <style>
    .hero-section {
        text-align: center;
        padding: 50px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .hero-title {
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .hero-subtitle {
        font-size: 1.5em;
        margin-bottom: 30px;
    }
    .feature-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px;
        text-align: center;
    }
    .cta-button {
        background: #ff6b6b;
        color: white;
        padding: 15px 30px;
        border: none;
        border-radius: 5px;
        font-size: 1.2em;
        margin: 10px;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">🚑 BioSync Tele-Rescue</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Autonomous Edge-AI Teleconsultation Platform</p>', unsafe_allow_html=True)
    st.markdown('<p>Revolutionizing emergency healthcare by automatically connecting patients to doctors during critical moments.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Key Features
    st.header("✨ Key Features")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
        <h3>🤖 AI-Powered Detection</h3>
        <p>Edge-AI wearables detect critical vitals anomalies in real-time</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
        <h3>🚨 Auto-Dial Emergency</h3>
        <p>Automatically initiates teleconsultation when anomalies are detected</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
        <h3>📹 Live Video & Vitals</h3>
        <p>Streams live patient vitals and video feed to available doctors</p>
        </div>
        """, unsafe_allow_html=True)

    # How It Works
    st.header("🔄 How It Works")
    st.markdown("""
    1. **Wear the Device**: Patients wear our edge-AI enabled wearable that monitors vital signs continuously.
    2. **AI Detection**: When critical anomalies are detected (cardiac events, falls, etc.), the system triggers automatically.
    3. **Auto-Connect**: The platform bypasses booking systems and directly connects to the nearest available emergency doctor.
    4. **Live Consultation**: Doctor receives live vitals feed, AI triage brief, and can initiate WebRTC video consultation.
    """)

    # Call to Action
    st.header("🚀 Get Started")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("👤 Access Patient Dashboard", key="patient_cta"):
            st.session_state.view = "👤 Patient Dashboard"
            st.rerun()

    with col2:
        if st.button("👨‍⚕️ Access Doctor Platform", key="doctor_cta"):
            st.session_state.view = "👨‍⚕️ Doctor Platform"
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("**BioSync Tele-Rescue** - Saving lives through autonomous teleconsultation")
    st.markdown("*Developed for HackArena 2K26 Healthcare Track*")

elif view == "👤 Patient Dashboard":
    st.header("Patient Vitals Monitoring")

    # Placeholder for vitals
    vitals_placeholder = st.empty()

    # Simulate normal monitoring
    if st.button("Simulate Normal Monitoring"):
        for _ in range(10):
            vitals = get_mock_vitals()
            with vitals_placeholder.container():
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Heart Rate", f"{vitals['Heart Rate']} bpm")
                col2.metric("SpO2", f"{vitals['SpO2']}%")
                col3.metric("Temperature", f"{vitals['Temperature']}°C")
                col4.metric("Blood Pressure", vitals['Blood Pressure'])
            time.sleep(1)

    # SOS Trigger
    if st.button("Simulate Emergency (SOS Trigger)"):
        st.error("🚨 CRITICAL ALERT: Anomaly Detected!")
        st.warning("Auto-Dialing Available Doctor...")
        # Mock WebRTC placeholder
        st.image("https://via.placeholder.com/640x480?text=WebRTC+Video+Feed", caption="Mock WebRTC Video Call")

elif view == "👨‍⚕️ Doctor Platform":
    # Modern Healthcare Dashboard CSS
    st.markdown("""
    <style>
    /* Modern Healthcare Dashboard Styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }

    .overview-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #4A90E2;
        margin: 10px 0;
        transition: transform 0.2s ease;
    }

    .overview-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }

    .emergency-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #E74C3C;
        margin: 10px 0;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3); }
        50% { box-shadow: 0 4px 15px rgba(231, 76, 60, 0.6); }
        100% { box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3); }
    }

    .chart-container {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 20px 0;
    }

    .activity-item {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 4px solid #28a745;
    }

    .appointment-item {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        color: #2c3e50;
    }

    .metric-label {
        font-size: 0.9em;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .sidebar-nav {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }

    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }

    .status-completed { background: #d4edda; color: #155724; }
    .status-progress { background: #fff3cd; color: #856404; }
    .status-emergency { background: #f8d7da; color: #721c24; }

    .soft-green { color: #28a745; }
    .medical-blue { color: #4A90E2; }
    .emergency-red { color: #E74C3C; }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .overview-card, .chart-container {
            margin: 10px 0;
        }
        .main-header {
            padding: 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Main Header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.2em;">🏥 Doctor Consultation Dashboard</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Welcome back, Dr. Smith • Last login: Today 8:00 AM</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation (keeping the existing sidebar structure)
    st.sidebar.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
    st.sidebar.markdown("### 🧭 Navigation")
    nav_options = ["📊 Dashboard", "📅 Appointments", "👥 Patients", "📈 Reports", "🚨 Emergency"]
    selected_nav = st.sidebar.radio("", nav_options, index=0, label_visibility="collapsed")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Dashboard Content
    if selected_nav == "📊 Dashboard":
        # Overview Cards Row
        st.markdown("### 📈 Overview")
        col1, col2, col3, col4 = st.columns(4)

        dashboard_data = get_dashboard_data()

        with col1:
            st.markdown(f"""
            <div class="overview-card">
                <div class="metric-value medical-blue">{dashboard_data['total_consultations']}</div>
                <div class="metric-label">Total Consultations</div>
                <p style="color: #28a745; margin: 5px 0;">↗️ +12% this month</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="overview-card">
                <div class="metric-value medical-blue">{dashboard_data['active_patients']}</div>
                <div class="metric-label">Active Patients</div>
                <p style="color: #28a745; margin: 5px 0;">↗️ +5% this week</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="emergency-card">
                <div class="metric-value emergency-red">{dashboard_data['emergency_cases']}</div>
                <div class="metric-label">Emergency Cases</div>
                <p style="color: #E74C3C; margin: 5px 0;">⚠️ Requires immediate attention</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="overview-card">
                <div class="metric-value medical-blue">{dashboard_data['today_appointments']}</div>
                <div class="metric-label">Today's Appointments</div>
                <p style="color: #28a745; margin: 5px 0;">✅ All scheduled</p>
            </div>
            """, unsafe_allow_html=True)

        # Charts Section
        st.markdown("### 📊 Analytics")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 📈 Consultation Trends")

            # Generate sample data for line chart
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            consultations = np.random.randint(5, 25, size=30)
            df_trends = pd.DataFrame({'Date': dates, 'Consultations': consultations})

            st.line_chart(df_trends.set_index('Date'))
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 🥧 Patient Categories")

            # Sample pie chart data
            categories = ['Cardiology', 'Emergency', 'General', 'Neurology', 'Pediatrics']
            values = [35, 25, 20, 12, 8]

            fig_pie = {
                'data': [{
                    'values': values,
                    'labels': categories,
                    'type': 'pie',
                    'marker': {'colors': ['#4A90E2', '#E74C3C', '#28a745', '#F39C12', '#9B59B6']}
                }],
                'layout': {
                    'showlegend': True,
                    'height': 300,
                    'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0}
                }
            }
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Bottom Row: Recent Activity and Upcoming Appointments
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 🕒 Recent Activity")

            activities = get_recent_activity()
            for activity in activities:
                status_class = {
                    "Completed": "status-completed",
                    "In Progress": "status-progress",
                    "Emergency": "status-emergency"
                }.get(activity['status'], "status-completed")

                st.markdown(f"""
                <div class="activity-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{activity['patient']}</strong><br>
                            <small style="color: #6c757d;">{activity['time']} • {activity['type']}</small>
                        </div>
                        <span class="status-badge {status_class}">{activity['status']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 📅 Upcoming Appointments")

            appointments = get_upcoming_appointments()
            for appointment in appointments:
                st.markdown(f"""
                <div class="appointment-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{appointment['time']}</strong> - {appointment['patient']}<br>
                            <small style="color: #6c757d;">{appointment['type']}</small>
                        </div>
                        <button style="background: #4A90E2; color: white; border: none; padding: 5px 15px; border-radius: 5px; cursor: pointer;">Join Call</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # Emergency Alert Panel
        st.markdown("### 🚨 Emergency Alert Panel")
        st.markdown("""
        <div class="emergency-card">
            <h4 style="color: #E74C3C; margin-top: 0;">⚠️ Critical Cases Requiring Attention</h4>
            <div style="display: flex; gap: 20px; margin-top: 15px;">
                <div style="flex: 1;">
                    <strong>Patient: Sarah Wilson</strong><br>
                    <small>Cardiac arrest detected • 2 min ago</small><br>
                    <span style="color: #E74C3C;">🚨 Emergency consultation initiated</span>
                </div>
                <div style="flex: 1;">
                    <strong>Patient: Mike Johnson</strong><br>
                    <small>Severe chest pain • 5 min ago</small><br>
                    <span style="color: #E74C3C;">🚨 Auto-dialing emergency doctor</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Patient Insights
        st.markdown("### 📊 Patient Insights")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("""
            <div class="overview-card">
                <div style="text-align: center;">
                    <div style="font-size: 2em; color: #28a745;">💓</div>
                    <div class="metric-value">87%</div>
                    <div class="metric-label">Avg Heart Rate</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="overview-card">
                <div style="text-align: center;">
                    <div style="font-size: 2em; color: #4A90E2;">🫁</div>
                    <div class="metric-value">96%</div>
                    <div class="metric-label">Avg SpO2</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="overview-card">
                <div style="text-align: center;">
                    <div style="font-size: 2em; color: #F39C12;">🌡️</div>
                    <div class="metric-value">36.8°C</div>
                    <div class="metric-label">Avg Temperature</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div class="overview-card">
                <div style="text-align: center;">
                    <div style="font-size: 2em; color: #9B59B6;">⚡</div>
                    <div class="metric-value">23</div>
                    <div class="metric-label">Alerts Today</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    elif selected_nav == "🚨 Emergency":
        st.markdown("### 🚨 Emergency Cases")
        st.markdown("""
        <div class="emergency-card">
            <h3>Active Emergency Consultations</h3>
            <p>Real-time emergency cases requiring immediate attention.</p>
        </div>
        """, unsafe_allow_html=True)

        # Live Emergency Feed
        st.subheader("Live Patient Vitals Feed")
        vitals_feed = st.empty()

        if st.button("Start Emergency Vitals Feed"):
            for _ in range(20):
                vitals = get_mock_vitals()
                with vitals_feed.container():
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Heart Rate", f"{vitals['Heart Rate']} bpm")
                    col2.metric("SpO2", f"{vitals['SpO2']}%")
                    col3.metric("Temperature", f"{vitals['Temperature']}°C")
                    col4.metric("Blood Pressure", vitals['Blood Pressure'])
                time.sleep(0.5)

        # AI Triage Brief
        st.subheader("🤖 AI Triage Brief")
        st.info("**Suspected cardiac event detected.** Immediate CPR and defibrillation recommended. Patient showing critical vitals drop - auto-dialing emergency response team.")

    else:
        st.info(f"📋 {selected_nav} section coming soon...")

st.sidebar.markdown("---")
st.sidebar.markdown("**BioSync Tele-Rescue** - Emergency Teleconsultation")
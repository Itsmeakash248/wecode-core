"""
BioSync Tele-Rescue - Pages Module
Organized page components for the healthcare dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from .data_manager import data_manager
from .ui_components import ui
from .webrtc_consultation import consultation_module
from .live_platform import render_doctor_dashboard, render_patient_dashboard


class LandingPage:
    """Landing page component"""

    @staticmethod
    def render():
        """Render the landing page"""
        st.markdown("""
        <style>
        .hero-section {
            text-align: center;
            padding: 60px 40px;
            background: linear-gradient(135deg, #2563eb 0%, #7c3aed 50%, #0d9488 100%);
            color: white;
            border-radius: 24px;
            margin-bottom: 40px;
            box-shadow: 0 12px 48px rgba(37, 99, 235, 0.25);
            position: relative;
            overflow: hidden;
        }

        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="hero-pattern" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="30" cy="30" r="0.5" fill="rgba(255,255,255,0.15)"/></pattern></defs><rect width="100" height="100" fill="url(%23hero-pattern)"/></svg>');
            opacity: 0.3;
        }

        .hero-title {
            font-size: 3.5em;
            font-weight: 800;
            margin-bottom: 24px;
            text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            position: relative;
            z-index: 1;
        }

        .hero-subtitle {
            font-size: 1.8em;
            margin-bottom: 36px;
            font-weight: 300;
            opacity: 0.95;
            position: relative;
            z-index: 1;
        }

        .feature-card {
            background: linear-gradient(135deg, white 0%, #f9fafb 100%);
            padding: 32px;
            border-radius: 18px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin: 20px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid #e5e7eb;
            position: relative;
            overflow: hidden;
        }

        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 120px;
            height: 120px;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(13, 148, 136, 0.05) 100%);
            border-radius: 50%;
            transform: translate(40px, -40px);
        }

        .feature-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
        }

        .feature-card h3 {
            color: #1f2937;
            font-size: 1.4em;
            font-weight: 700;
            margin-bottom: 16px;
            position: relative;
            z-index: 1;
        }

        .feature-card p {
            color: #6b7280;
            font-size: 1em;
            line-height: 1.6;
            position: relative;
            z-index: 1;
        }

        .cta-button {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            padding: 16px 32px;
            border: none;
            border-radius: 12px;
            font-size: 1.2em;
            font-weight: 600;
            margin: 12px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: relative;
            overflow: hidden;
        }

        .cta-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }

        .cta-button:hover::before {
            left: 100%;
        }

        .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(37, 99, 235, 0.4);
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        }

        .stats-section {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 40px;
            border-radius: 20px;
            margin: 40px 0;
            text-align: center;
            border: 1px solid #e2e8f0;
        }

        .stat-item {
            display: inline-block;
            margin: 20px 40px;
            text-align: center;
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: 800;
            color: #2563eb;
            margin-bottom: 8px;
            text-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
        }

        .stat-label {
            font-size: 1em;
            color: #64748b;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.5em;
            }
            .hero-subtitle {
                font-size: 1.3em;
            }
            .feature-card {
                margin: 15px;
                padding: 24px;
            }
            .stat-item {
                margin: 15px 20px;
            }
            .stat-number {
                font-size: 2em;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        # Hero Section
        st.markdown('<div class="hero-section">', unsafe_allow_html=True)
        col_l, col_m, col_r = st.columns([1, 1, 1])
        with col_m:
            st.image("animation.gif", width=160)
        st.markdown('<h1 class="hero-title">🚑 BioSync Tele-Rescue</h1>', unsafe_allow_html=True)
        st.markdown('<p class="hero-subtitle">Autonomous Edge-AI Teleconsultation Platform</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 1.1em; opacity: 0.9;">Revolutionizing emergency healthcare by automatically connecting patients to doctors during critical moments through advanced AI-powered wearables.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Statistics Section
        st.markdown("""
        <div class="stats-section">
            <div class="stat-item">
                <div class="stat-number">30s</div>
                <div class="stat-label">Avg Response Time</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">95%</div>
                <div class="stat-label">Accuracy Rate</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">24/7</div>
                <div class="stat-label">Monitoring</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">10k+</div>
                <div class="stat-label">Lives Saved</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Key Features
        st.header("✨ Advanced Features")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="feature-card">
            <h3>🤖 Edge-AI Detection</h3>
            <p>Advanced machine learning algorithms running on wearable devices detect critical vital sign anomalies in real-time with 95% accuracy.</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="feature-card">
            <h3>🚨 Auto-Emergency Dial</h3>
            <p>Bypasses traditional booking systems to automatically connect patients with the nearest available emergency specialist within 30 seconds.</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="feature-card">
            <h3>📹 Live HD Streaming</h3>
            <p>Streams high-definition patient vitals and video feed to doctors, enabling comprehensive remote diagnosis and treatment guidance.</p>
            </div>
            """, unsafe_allow_html=True)

        # Additional Features Row
        col4, col5, col6 = st.columns(3)

        with col4:
            st.markdown("""
            <div class="feature-card">
            <h3>🔒 HIPAA Compliant</h3>
            <p>End-to-end encryption ensures all patient data and communications remain secure and compliant with healthcare privacy regulations.</p>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            st.markdown("""
            <div class="feature-card">
            <h3>📊 Real-time Analytics</h3>
            <p>Advanced dashboard provides doctors with comprehensive patient analytics, trend analysis, and predictive health insights.</p>
            </div>
            """, unsafe_allow_html=True)

        with col6:
            st.markdown("""
            <div class="feature-card">
            <h3>🌐 Global Network</h3>
            <p>Connects patients with healthcare professionals worldwide, ensuring access to specialized care regardless of location.</p>
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
            if st.button("👤 Access Patient Dashboard", key="patient_cta", help="Monitor your health vitals"):
                st.session_state.view = "👤 Patient Dashboard"
                st.rerun()

        with col2:
            if st.button("👨‍⚕️ Access Doctor Platform", key="doctor_cta", help="Access telemedicine dashboard"):
                st.session_state.view = "👨‍⚕️ Doctor Platform"
                st.rerun()

        # Footer
        st.markdown("---")
        st.markdown("**BioSync Tele-Rescue** - Saving lives through autonomous teleconsultation")
        st.markdown("*Developed for HackArena 2K26 Healthcare Track*")


class PatientDashboard:
    """Patient dashboard component"""

    @staticmethod
    def render(auth_user=None):
        """Render the patient dashboard"""
        render_patient_dashboard(auth_user=auth_user)

    @staticmethod
    def _render_feedback_section():
        """Render patient feedback form and recent submissions."""
        st.markdown("### ⭐ Patient Feedback")
        st.caption("Share your consultation experience to help us improve care quality.")

        patient_names = [patient["name"] for patient in data_manager.patients]
        doctor_names = [doctor["name"] for doctor in data_manager.doctors]

        with st.form("patient_feedback_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                selected_patient = st.selectbox("Patient Name", patient_names, key="feedback_patient")
                selected_doctor = st.selectbox("Consulting Doctor", doctor_names, key="feedback_doctor")
                consultation_type = st.selectbox(
                    "Consultation Type",
                    ["Emergency", "Follow-up", "Consultation", "Checkup", "Therapy"],
                    key="feedback_type",
                )

            with col2:
                overall_rating = st.slider("Overall Rating", min_value=1, max_value=5, value=5, key="feedback_rating")
                communication_rating = st.slider("Communication Quality", min_value=1, max_value=5, value=5, key="feedback_communication")
                wait_time_rating = st.slider("Wait Time Experience", min_value=1, max_value=5, value=4, key="feedback_wait_time")

            recommend = st.checkbox("I would recommend this doctor/service", value=True, key="feedback_recommend")
            comments = st.text_area(
                "Additional Comments",
                placeholder="Describe what worked well and what can be improved...",
                key="feedback_comments",
            )

            submitted = st.form_submit_button("📨 Submit Feedback", type="primary")

            if submitted:
                if not comments.strip():
                    st.warning("Please add a short comment before submitting feedback.")
                else:
                    data_manager.submit_feedback(
                        patient=selected_patient,
                        doctor=selected_doctor,
                        consultation_type=consultation_type,
                        rating=overall_rating,
                        communication=communication_rating,
                        wait_time=wait_time_rating,
                        recommend=recommend,
                        comments=comments,
                    )
                    st.success("Thank you. Your feedback has been recorded successfully.")

        st.markdown("#### 🕒 Recent Feedback Submitted")
        recent_feedback = data_manager.get_feedback_entries()[:5]

        if not recent_feedback:
            st.info("No feedback submitted yet.")
            return

        for item in recent_feedback:
            recommend_text = "Yes" if item["recommend"] else "No"
            with st.expander(
                f"{item['patient']} • {item['doctor']} • {item['rating']}/5 • {item['created_at']}",
                expanded=False,
            ):
                st.markdown(f"**Type:** {item['consultation_type']}")
                st.markdown(f"**Communication:** {item['communication']}/5")
                st.markdown(f"**Wait Time:** {item['wait_time']}/5")
                st.markdown(f"**Would Recommend:** {recommend_text}")
                st.markdown(f"**Comment:** {item['comments']}")


class DoctorDashboard:
    """Doctor dashboard component"""

    @staticmethod
    def render(auth_user=None):
        """Render the doctor dashboard"""
        render_doctor_dashboard(auth_user=auth_user)

    @staticmethod
    def _render_main_dashboard():
        """Render the main dashboard view"""
        # Create main layout with left content and right metrics sidebar
        main_col, metrics_col = st.columns([3, 1])

        with main_col:
            st.markdown("### 📈 Overview")
            metrics = data_manager.get_dashboard_metrics()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                ui.create_metric_card("Total Consultations", str(metrics['total_consultations']), "↗️ +12% this month")
            with col2:
                ui.create_metric_card("Active Patients", str(metrics['active_patients']), "↗️ +5% this week")
            with col3:
                ui.create_metric_card("Emergency Cases", str(metrics['emergency_cases']), "⚠️ Requires attention", "emergency")
            with col4:
                ui.create_metric_card("Today's Appointments", str(metrics['today_appointments']), "✅ All scheduled", "success")

            st.markdown("### 👨‍⚕️ Doctor Listing & Availability Status")
            filter_col, stats_col = st.columns([2, 3])

            with filter_col:
                status_filter = st.selectbox(
                    "Filter by Availability",
                    ["All", "Available", "Busy", "Offline"],
                    key="doctor_status_filter"
                )

            with stats_col:
                counts = data_manager.get_doctor_availability_counts()
                st.markdown(
                    f"""
                    <div style="padding: 10px 14px; border: 1px solid #e5e7eb; border-radius: 12px; background: #f8fafc; margin-top: 28px;">
                        <strong>Summary:</strong>
                        🟢 {counts['available']} Available &nbsp;|&nbsp;
                        🟠 {counts['busy']} Busy &nbsp;|&nbsp;
                        ⚪ {counts['offline']} Offline &nbsp;|&nbsp;
                        👥 {counts['total']} Total
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            listed_doctors = data_manager.get_doctor_listing(status_filter)
            if listed_doctors:
                for doctor in listed_doctors:
                    ui.create_doctor_availability_item(
                        name=doctor['name'],
                        specialty=doctor['specialty'],
                        status=doctor['status'],
                        rating=doctor['rating'],
                        experience=doctor['experience']
                    )
            else:
                st.info("No doctors found for the selected availability filter.")

        # Charts Section
        st.markdown("### 📊 Analytics")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 📈 Consultation Trends")

            trends_df = data_manager.get_consultation_trends()
            fig = px.area(trends_df, x='Date', y='Consultations',
                         title='Daily Consultations (Last 30 Days)',
                         color_discrete_sequence=['#2563eb'],
                         pattern_shape_sequence=[""],
                         fill='tozeroy')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#374151',
                title_font_size=16,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False,
                height=300
            )
            fig.update_traces(line=dict(width=3))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 🥧 Patient Categories")

            categories = data_manager.get_patient_categories()
            colors = ['#2563eb', '#059669', '#d97706', '#dc2626', '#7c3aed']
            fig = px.pie(values=list(categories.values()), names=list(categories.keys()),
                        title='Patient Distribution by Category',
                        color_discrete_sequence=colors)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#374151',
                title_font_size=16,
                margin=dict(l=20, r=20, t=40, b=20),
                height=300
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Additional Analytics Row
        st.markdown("### 📊 Advanced Analytics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### ⏱️ Response Time Distribution")

            response_times = pd.DataFrame({
                'Time Range': ['< 5 min', '5-10 min', '10-15 min', '15-30 min', '> 30 min'],
                'Cases': [45, 32, 18, 8, 2]
            })

            fig = px.bar(response_times, x='Time Range', y='Cases',
                        title='Emergency Response Times',
                        color='Cases',
                        color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#374151',
                title_font_size=14,
                margin=dict(l=20, r=20, t=40, b=20),
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 🌍 Geographic Distribution")

            geo_data = pd.DataFrame({
                'Region': ['North', 'South', 'East', 'West', 'Central'],
                'Patients': [120, 95, 78, 65, 42]
            })

            fig = px.bar(geo_data, x='Region', y='Patients',
                        title='Patients by Region',
                        color='Patients',
                        color_continuous_scale='Blues')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#374151',
                title_font_size=14,
                margin=dict(l=20, r=20, t=40, b=20),
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 📊 Consultation Types")

            consult_types = pd.DataFrame({
                'Type': ['Emergency', 'Follow-up', 'Consultation', 'Screening'],
                'Count': [156, 89, 234, 67]
            })

            fig = px.pie(consult_types, values='Count', names='Type',
                        title='Consultation Types Distribution',
                        color_discrete_sequence=['#dc2626', '#d97706', '#2563eb', '#059669'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#374151',
                title_font_size=14,
                margin=dict(l=20, r=20, t=40, b=20),
                height=250
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Bottom Row: Recent Activity and Upcoming Appointments
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 🕒 Recent Activity")

            activities = data_manager.get_recent_activity()
            for activity in activities:
                ui.create_activity_item(
                    activity['patient'], activity['time'],
                    activity['status'], activity['type'], activity['doctor']
                )

            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 📅 Upcoming Appointments")

            appointments = data_manager.get_upcoming_appointments()
            for appointment in appointments:
                ui.create_appointment_item(
                    appointment['time'], appointment['patient'],
                    appointment['type'], appointment['doctor']
                )

            st.markdown('</div>', unsafe_allow_html=True)

        # Emergency Alert Panel with Enhanced UI
        st.markdown("### 🚨 Emergency Alert Panel")

        # Emergency Status Overview
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ui.create_metric_card("Active Alerts", "3", "Critical cases", "emergency")
        with col2:
            ui.create_metric_card("Avg Response", "4.2 min", "This month", "success")
        with col3:
            ui.create_metric_card("Success Rate", "96%", "Emergency saves", "success")
        with col4:
            ui.create_metric_card("AI Accuracy", "95%", "Detection rate", "success")

        alerts = data_manager.get_emergency_alerts()
        for alert in alerts:
            ui.create_emergency_alert(
                alert['patient'], alert['condition'], alert['time'],
                alert['severity'], alert['action']
            )

        # Patient Insights with Enhanced Cards
        st.markdown("### 📊 Patient Insights")
        col1, col2, col3, col4 = st.columns(4)

        insights = data_manager.get_patient_insights()
        for i, insight in enumerate(insights):
            with [col1, col2, col3, col4][i]:
                ui.create_insight_card(
                    insight['icon'], insight['value'],
                    insight['metric'], insight['color']
                )

        # Quick Actions Panel
        st.markdown("### ⚡ Quick Actions")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📞 Emergency Call", key="emergency_call", type="primary"):
                ui.create_notification("Connecting to emergency patient...", "warning")
        with col2:
            if st.button("📋 Generate Report", key="quick_report"):
                ui.create_notification("Generating patient report...", "info")
        with col3:
            if st.button("👥 Team Consultation", key="team_consult"):
                ui.create_notification("Initiating team consultation...", "info")
        with col4:
            if st.button("📊 Analytics View", key="analytics_view"):
                ui.create_notification("Switching to analytics view...", "info")

        # Right Side Metrics Panel
        with metrics_col:
            DoctorDashboard._render_current_metrics_sidebar()

    @staticmethod
    def _render_doctor_availability_sidebar():
        """Render compact doctor availability list in the sidebar."""
        online_doctors = data_manager.get_doctor_listing("Available")
        st.sidebar.caption(f"Online now: {len(online_doctors)}")

        if not online_doctors:
            st.sidebar.info("No doctors online right now")
            return

        with st.sidebar:
            for doctor in online_doctors:
                ui.create_doctor_availability_item(
                    name=doctor['name'],
                    specialty=doctor['specialty'],
                    status=doctor['status'],
                    rating=doctor['rating'],
                    experience=doctor['experience'],
                    compact=True
                )

    def _render_appointments():
        """Render appointments management"""
        st.markdown("### 📅 Appointments Management")

        # Today's Schedule
        st.subheader("📋 Today's Schedule")
        schedule = data_manager.get_doctor_schedule(1)  # Doctor ID 1

        for slot in schedule:
            if slot['patient'] == "Available":
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 5px 0; border-left: 4px solid #28a745;">
                    <strong>{slot['time']}</strong> - {slot['patient']} ({slot['type']})
                </div>
                """, unsafe_allow_html=True)
            elif slot['patient'] == "Lunch Break":
                st.markdown(f"""
                <div style="background: #fff3cd; padding: 15px; border-radius: 10px; margin: 5px 0; border-left: 4px solid #F39C12;">
                    <strong>{slot['time']}</strong> - {slot['patient']} ({slot['type']})
                </div>
                """, unsafe_allow_html=True)
            else:
                ui.create_appointment_item(slot['time'], slot['patient'], slot['type'])

        # Appointment Actions
        st.subheader("⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("➕ Schedule New Appointment", key="schedule_new"):
                ui.create_notification("Appointment scheduling feature coming soon!", "info")

        with col2:
            if st.button("📝 Reschedule Appointment", key="reschedule"):
                ui.create_notification("Rescheduling feature coming soon!", "info")

        with col3:
            if st.button("❌ Cancel Appointment", key="cancel"):
                ui.create_notification("Cancellation feature coming soon!", "warning")

    @staticmethod
    def _render_patients():
        """Render patient management"""
        st.markdown("### 👥 Patient Management")

        # Search functionality
        search_query = st.text_input("🔍 Search Patients", placeholder="Search by name or condition...")

        patients = data_manager.search_patients(search_query) if search_query else data_manager.patients

        if patients:
            for patient in patients:
                with st.expander(f"👤 {patient['name']} - {patient['condition']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Age", f"{patient['age']} years")
                    with col2:
                        st.metric("Last Visit", patient['last_visit'])
                    with col3:
                        risk_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(patient['risk_level'], "⚪")
                        st.metric("Risk Level", f"{risk_color} {patient['risk_level']}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"📞 Call {patient['name']}", key=f"call_{patient['id']}"):
                            st.success(f"Initiating call with {patient['name']}...")
                    with col2:
                        if st.button(f"📋 View Records", key=f"records_{patient['id']}"):
                            st.info(f"Opening medical records for {patient['name']}...")
        else:
            st.info("No patients found matching your search.")

    @staticmethod
    def _render_consultation():
        """Render doctor consultation center with WebRTC and room chat."""
        st.markdown("### 💬 Consultation Center")
        st.caption("Use the same room ID as the patient to join the live teleconsultation.")

        default_room = st.session_state.get("active_consultation_room_patient", "ER-001")
        consultation_module.render(
            role="Doctor",
            default_room_id=default_room,
            section_title="Doctor Consultation Room (WebRTC)"
        )

    @staticmethod
    def _render_feedback_dashboard():
        """Render doctor-facing patient feedback analytics and review center."""
        st.markdown("### ⭐ Patient Feedback Center")

        doctor_options = ["All"] + [doctor["name"] for doctor in data_manager.doctors]
        col1, col2, col3 = st.columns(3)

        with col1:
            doctor_filter = st.selectbox("Doctor Filter", doctor_options, key="feedback_doctor_filter")
        with col2:
            min_rating = st.selectbox("Minimum Rating", [1, 2, 3, 4, 5], index=0, key="feedback_min_rating")
        with col3:
            recent_days = st.selectbox("Time Window", [7, 14, 30, 90], index=1, key="feedback_recent_days")

        summary = data_manager.get_feedback_summary(doctor_filter)

        metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
        with metric_col1:
            st.metric("Total Feedback", summary["total_feedback"])
        with metric_col2:
            st.metric("Avg Rating", f"{summary['avg_rating']}/5")
        with metric_col3:
            st.metric("Communication", f"{summary['avg_communication']}/5")
        with metric_col4:
            st.metric("Wait Time", f"{summary['avg_wait_time']}/5")
        with metric_col5:
            st.metric("Recommend Rate", f"{summary['recommend_percent']}%")

        if summary["low_ratings"] > 0:
            st.warning(f"{summary['low_ratings']} low-rating feedback entries (<=2 stars) need review.")
        else:
            st.success("No critical low-rating feedback in current dataset.")

        filtered_entries = data_manager.get_feedback_entries(
            doctor_filter=doctor_filter,
            min_rating=min_rating,
            recent_days=recent_days,
        )

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("#### Rating Distribution")
            distribution = data_manager.get_feedback_rating_distribution(doctor_filter)
            dist_df = pd.DataFrame(
                {"Stars": list(distribution.keys()), "Count": list(distribution.values())}
            )
            fig_dist = px.bar(
                dist_df,
                x="Stars",
                y="Count",
                color="Stars",
                color_discrete_sequence=["#ef4444", "#f97316", "#f59e0b", "#10b981", "#2563eb"],
                title="Feedback by Star Rating",
            )
            fig_dist.update_layout(showlegend=False, height=320)
            st.plotly_chart(fig_dist, use_container_width=True)

        with chart_col2:
            st.markdown("#### Feedback Trend (14 Days)")
            trend_df = data_manager.get_feedback_trends(doctor_filter=doctor_filter, days=14)
            fig_trend = px.line(
                trend_df,
                x="Date",
                y="Avg Rating",
                markers=True,
                title="Average Rating Over Time",
                color_discrete_sequence=["#2563eb"],
            )
            fig_trend.update_layout(yaxis_range=[0, 5], height=320)
            st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("#### Detailed Feedback")
        if not filtered_entries:
            st.info("No feedback matches the current filters.")
            return

        feedback_df = pd.DataFrame(filtered_entries)
        feedback_df = feedback_df.rename(
            columns={
                "created_at": "Submitted At",
                "consultation_type": "Type",
                "communication": "Communication",
                "wait_time": "Wait Time",
                "recommend": "Recommend",
                "comments": "Comments",
                "patient": "Patient",
                "doctor": "Doctor",
                "rating": "Rating",
            }
        )
        feedback_df["Recommend"] = feedback_df["Recommend"].map({True: "Yes", False: "No"})

        st.dataframe(
            feedback_df[
                [
                    "Submitted At",
                    "Patient",
                    "Doctor",
                    "Type",
                    "Rating",
                    "Communication",
                    "Wait Time",
                    "Recommend",
                    "Comments",
                ]
            ],
            use_container_width=True,
        )

    @staticmethod
    def _render_reports():
        """Render reports and analytics"""
        st.markdown("### 📈 Reports & Analytics")

        # Report Type Selection
        report_type = st.selectbox("Select Report Type",
                                  ["Consultation Summary", "Patient Demographics", "Patient Feedback", "Emergency Response", "Revenue Report"])

        if report_type == "Consultation Summary":
            st.subheader("📊 Consultation Summary Report")

            # Mock data for demonstration
            report_data = {
                'Total Consultations': 1247,
                'Emergency Cases': 89,
                'Average Response Time': '4.2 min',
                'Patient Satisfaction': '4.8/5',
                'Success Rate': '96%'
            }

            col1, col2 = st.columns(2)
            for i, (key, value) in enumerate(report_data.items()):
                with [col1, col2][i % 2]:
                    ui.create_metric_card(key, value)

        elif report_type == "Patient Demographics":
            st.subheader("👥 Patient Demographics")

            # Age distribution chart
            age_data = pd.DataFrame({
                'Age Group': ['18-30', '31-50', '51-70', '70+'],
                'Count': [45, 120, 89, 34]
            })

            fig = px.bar(age_data, x='Age Group', y='Count',
                        title='Patient Distribution by Age Group',
                        color='Count', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

        elif report_type == "Patient Feedback":
            st.subheader("⭐ Patient Feedback Report")
            summary = data_manager.get_feedback_summary()

            report_col1, report_col2, report_col3, report_col4 = st.columns(4)
            with report_col1:
                ui.create_metric_card("Total Feedback", str(summary["total_feedback"]), "All submitted entries")
            with report_col2:
                ui.create_metric_card("Avg Rating", f"{summary['avg_rating']}/5", "Overall patient score")
            with report_col3:
                ui.create_metric_card("Recommend Rate", f"{summary['recommend_percent']}%", "Would recommend service")
            with report_col4:
                ui.create_metric_card("Low Ratings", str(summary["low_ratings"]), "Needs quality follow-up")

            trend_df = data_manager.get_feedback_trends(days=30)
            fig = px.line(
                trend_df,
                x="Date",
                y="Avg Rating",
                markers=True,
                title="30-Day Patient Feedback Trend",
                color_discrete_sequence=["#2563eb"],
            )
            fig.update_layout(yaxis_range=[0, 5])
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info(f"{report_type} report feature coming soon!")

        # Export Options
        st.subheader("📤 Export Options")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Export PDF", key="export_pdf"):
                ui.create_notification("PDF export feature coming soon!", "info")

        with col2:
            if st.button("📊 Export Excel", key="export_excel"):
                ui.create_notification("Excel export feature coming soon!", "info")

        with col3:
            if st.button("📧 Email Report", key="email_report"):
                ui.create_notification("Email report feature coming soon!", "info")

    @staticmethod
    def _render_emergency():
        """Render emergency management"""
        st.markdown("### 🚨 Emergency Management Center")

        # Emergency Cases Overview with Enhanced Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ui.create_metric_card("Active Cases", "3", "Critical emergencies", "emergency")
        with col2:
            ui.create_metric_card("Avg Response", "4.2 min", "Target: <5 min", "success")
        with col3:
            ui.create_metric_card("Success Rate", "96%", "Lives saved", "success")
        with col4:
            ui.create_metric_card("AI Confidence", "95%", "Detection accuracy", "success")

        # Live Emergency Feed with Enhanced UI
        st.subheader("📹 Live Emergency Vitals Feed")

        vitals_placeholder = st.empty()

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("▶️ Start Emergency Feed", key="start_emergency_feed", type="primary"):
                st.session_state.emergency_feed = True
                ui.create_notification("Emergency monitoring activated!", "warning")

        with col2:
            if st.button("⏹️ Stop Feed", key="stop_emergency_feed"):
                st.session_state.emergency_feed = False
                ui.create_notification("Emergency feed stopped", "info")

        with col3:
            ui.create_metric_card("Monitor Status", "🟢 Active" if st.session_state.get('emergency_feed', False) else "🔴 Inactive",
                                "Real-time monitoring")

        if st.session_state.get('emergency_feed', False):
            with vitals_placeholder.container():
                vitals = data_manager.get_vitals_data()

                # Critical Vitals Display
                col1, col2, col3 = st.columns(3)

                with col1:
                    hr_status = "emergency" if vitals['Heart Rate'] > 120 else "success"
                    ui.create_metric_card("Heart Rate", f"{vitals['Heart Rate']} bpm",
                                        "Critical: >120 bpm", hr_status)
                with col2:
                    spo2_status = "emergency" if vitals['SpO2'] < 90 else "success"
                    ui.create_metric_card("SpO2", f"{vitals['SpO2']}%",
                                        "Critical: <90%", spo2_status)
                with col3:
                    bp_status = "emergency" if "180/" in vitals['Blood Pressure'] else "success"
                    ui.create_metric_card("Blood Pressure", vitals['Blood Pressure'],
                                        "Critical: >180/120", bp_status)

                # Real-time Trend Chart
                st.subheader("📈 Real-time Vitals Trend")

                # Generate real-time data
                import time
                current_time = pd.Timestamp.now()
                time_points = pd.date_range(start=current_time - pd.Timedelta(minutes=10),
                                          end=current_time, freq='30s')

                # Simulate real-time vitals with some variation
                hr_trend = [vitals['Heart Rate'] + np.random.normal(0, 2) for _ in range(len(time_points))]
                spo2_trend = [vitals['SpO2'] + np.random.normal(0, 0.5) for _ in range(len(time_points))]

                trend_df = pd.DataFrame({
                    'Time': time_points,
                    'Heart Rate': hr_trend,
                    'SpO2': spo2_trend
                })

                fig = px.line(trend_df, x='Time', y=['Heart Rate', 'SpO2'],
                             title='Emergency Vitals - Last 10 Minutes',
                             color_discrete_sequence=['#dc2626', '#059669'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#374151',
                    title_font_size=16,
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

        # AI Triage Brief with Enhanced UI
        st.subheader("🤖 AI-Powered Triage Analysis")

        # AI Analysis Cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #dc2626;">
                <h4 style="color: #dc2626; margin: 0;">🔴 CRITICAL CONDITION</h4>
                <p style="margin: 10px 0; color: #374151;">Cardiac arrest with severe hypotension detected</p>
                <small style="color: #6b7280;">Confidence: 98%</small>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #d97706;">
                <h4 style="color: #d97706; margin: 0;">🟡 IMMEDIATE ACTION</h4>
                <p style="margin: 10px 0; color: #374151;">Start CPR and prepare defibrillation</p>
                <small style="color: #6b7280;">Priority: LIFE-THREATENING</small>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #059669;">
                <h4 style="color: #059669; margin: 0;">🟢 SUPPORT AVAILABLE</h4>
                <p style="margin: 10px 0; color: #374151;">Ambulance en route (2 min ETA)</p>
                <small style="color: #6b7280;">Resources: FULLY AVAILABLE</small>
            </div>
            """, unsafe_allow_html=True)

        # Emergency Actions with Enhanced UI
        st.subheader("⚡ Emergency Response Actions")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🚑 Dispatch Ambulance", key="dispatch_ambulance", type="primary"):
                ui.create_notification("🚑 Ambulance dispatched! ETA: 3 minutes", "success")

        with col2:
            if st.button("👥 Alert Emergency Team", key="alert_team"):
                ui.create_notification("🚨 Emergency response team alerted!", "warning")

        with col3:
            if st.button("📞 Contact Family", key="contact_family"):
                ui.create_notification("📱 Family notification sent via SMS", "info")

        with col4:
            if st.button("📋 Generate Report", key="generate_report"):
                ui.create_notification("📄 Emergency report generated and sent", "success")

        # Communication Panel
        st.subheader("📡 Communication Panel")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Quick Messages to Patient Family:**")
            message_options = [
                "Your loved one is receiving emergency care",
                "Doctor is attending to the emergency situation",
                "Ambulance is on the way",
                "Please remain calm, help is on the way"
            ]

            selected_message = st.selectbox("Select message:", message_options, key="family_message")
            if st.button("📤 Send Message", key="send_family_msg"):
                ui.create_notification(f"Message sent: {selected_message}", "info")

        with col2:
            st.markdown("**Hospital Coordination:**")
            hospital_options = [
                "Notify emergency department",
                "Prepare cardiac care unit",
                "Alert cardiology team",
                "Request immediate admission"
            ]

            selected_coord = st.selectbox("Coordinate with hospital:", hospital_options, key="hospital_coord")
            if st.button("🏥 Send Coordination", key="send_coord"):
                ui.create_notification(f"Hospital notified: {selected_coord}", "warning")

    @staticmethod
    @staticmethod
    def _render_current_metrics_sidebar():
        """Render the current metrics sidebar with real-time updates"""
        import time

        # Auto-refresh every 30 seconds
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = time.time()

        current_time = time.time()
        if current_time - st.session_state.last_refresh > 30:
            st.session_state.last_refresh = current_time
            st.rerun()

        st.markdown('<div class="metrics-sidebar">', unsafe_allow_html=True)

        # Header
        st.markdown('''
        <div class="metrics-header">
            <h3>📊 Current Metrics</h3>
            <p>Real-time System Status</p>
        </div>
        ''', unsafe_allow_html=True)

        # System Status Section
        st.markdown('<div class="metrics-section">', unsafe_allow_html=True)
        st.markdown('<h4>🖥️ System Status</h4>', unsafe_allow_html=True)

        metrics = data_manager.get_current_metrics()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Server Load", f"{metrics['server_load']}%", delta="2.1%")
            st.metric("Memory Usage", f"{metrics['memory_usage']}%", delta="-1.2%")
        with col2:
            st.metric("CPU Usage", f"{metrics['cpu_usage']}%", delta="0.8%")
            st.metric("Disk Usage", f"{metrics['disk_usage']}%", delta="0.1%")

        st.markdown('</div>', unsafe_allow_html=True)

        # Performance Metrics Section
        st.markdown('<div class="metrics-section">', unsafe_allow_html=True)
        st.markdown('<h4>⚡ Performance</h4>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Response Time", f"{metrics['response_time']}ms", delta="-5ms")
            st.metric("Uptime", f"{metrics['uptime']}%", delta="0.1%")
        with col2:
            st.metric("Error Rate", f"{metrics['error_rate']}%", delta="-0.2%")
            st.metric("Throughput", f"{metrics['throughput']} req/s", delta="12")

        st.markdown('</div>', unsafe_allow_html=True)

        # Emergency Status Section
        st.markdown('<div class="metrics-section">', unsafe_allow_html=True)
        st.markdown('<h4>🚨 Emergency Status</h4>', unsafe_allow_html=True)

        emergency_data = metrics['emergency_status']
        st.markdown(f'<div class="metrics-item">Active Alerts: <strong>{emergency_data["active_alerts"]}</strong></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metrics-item">Critical Cases: <strong>{emergency_data["critical_cases"]}</strong></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metrics-item">Available Staff: <strong>{emergency_data["available_staff"]}</strong></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Network Metrics Section
        st.markdown('<div class="metrics-section">', unsafe_allow_html=True)
        st.markdown('<h4>🌐 Network</h4>', unsafe_allow_html=True)

        network_data = metrics['network']
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Bandwidth", f"{network_data['bandwidth']} Mbps", delta="5")
            st.metric("Active Connections", f"{network_data['connections']}", delta="3")
        with col2:
            st.metric("Latency", f"{network_data['latency']}ms", delta="-2")
            st.metric("Packet Loss", f"{network_data['packet_loss']}%", delta="-0.1%")

        st.markdown('</div>', unsafe_allow_html=True)

        # Recent Alerts Section
        st.markdown('<div class="metrics-section">', unsafe_allow_html=True)
        st.markdown('<h4>🔔 Recent Alerts</h4>', unsafe_allow_html=True)

        alerts = metrics['recent_alerts']
        for alert in alerts:
            alert_class = f"alert-{alert['type'].lower()}"
            st.markdown(f'<div class="alert-item {alert_class}">{alert["message"]}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # System Health Indicators
        st.markdown('<div class="metrics-section">', unsafe_allow_html=True)
        st.markdown('<h4>❤️ System Health</h4>', unsafe_allow_html=True)

        health_indicators = metrics['health_indicators']
        for indicator in health_indicators:
            status_class = f"status-{indicator['status'].lower()}"
            st.markdown(f'''
            <div class="health-indicator">
                <span>{indicator['component']}</span>
                <span class="status {status_class}">{indicator['status'].upper()}</span>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Quick Stats
        st.markdown('<div class="metrics-section">', unsafe_allow_html=True)
        st.markdown('<h4>📈 Quick Stats</h4>', unsafe_allow_html=True)

        quick_stats = metrics['quick_stats']
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Patients", f"{quick_stats['total_patients']}", delta="5")
            st.metric("Active Sessions", f"{quick_stats['active_sessions']}", delta="2")
        with col2:
            st.metric("Completed Consults", f"{quick_stats['completed_consults']}", delta="3")
            st.metric("Avg Wait Time", f"{quick_stats['avg_wait_time']}min", delta="-1")

        st.markdown('</div>', unsafe_allow_html=True)

        # Last Updated
        st.markdown(f'<p style="text-align: center; color: var(--neutral-gray-500); font-size: 0.8em; margin-top: 20px;">Last updated: {time.strftime("%H:%M:%S")}</p>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

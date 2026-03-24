"""
BioSync Tele-Rescue - UI Components Module
Reusable UI components and styling for the healthcare dashboard
"""

import streamlit as st
from typing import Dict, List, Any, Optional


class UIComponents:
    """UI components and styling utilities"""

    @staticmethod
    def inject_global_css():
        """Inject global CSS styles"""
        st.markdown("""
        <style>
        /* Enhanced Healthcare Dashboard Styles with Sophisticated Color Palette */

        /* Color Variables */
        :root {
            --primary-blue: #2563eb;
            --primary-blue-light: #3b82f6;
            --primary-blue-dark: #1d4ed8;
            --secondary-teal: #0d9488;
            --secondary-teal-light: #14b8a6;
            --accent-purple: #7c3aed;
            --accent-purple-light: #8b5cf6;
            --success-green: #059669;
            --success-green-light: #10b981;
            --warning-orange: #d97706;
            --warning-orange-light: #f59e0b;
            --error-red: #dc2626;
            --error-red-light: #ef4444;
            --neutral-gray-50: #f9fafb;
            --neutral-gray-100: #f3f4f6;
            --neutral-gray-200: #e5e7eb;
            --neutral-gray-300: #d1d5db;
            --neutral-gray-600: #4b5563;
            --neutral-gray-700: #374151;
            --neutral-gray-800: #1f2937;
            --neutral-gray-900: #111827;
        }

        .main-header {
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--accent-purple) 50%, var(--secondary-teal) 100%);
            color: white;
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(37, 99, 235, 0.2);
            position: relative;
            overflow: hidden;
        }

        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.15)"/><circle cx="90" cy="40" r="0.5" fill="rgba(255,255,255,0.15)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.1;
        }

        .main-header h1, .main-header h2, .main-header p {
            position: relative;
            z-index: 1;
        }

        .metric-card {
            background: linear-gradient(135deg, white 0%, var(--neutral-gray-50) 100%);
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border-left: 6px solid var(--primary-blue);
            margin: 12px 0;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            border: 1px solid var(--neutral-gray-200);
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100px;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(124, 58, 237, 0.05) 100%);
            border-radius: 50%;
            transform: translate(30px, -30px);
        }

        .metric-card:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
            border-color: var(--primary-blue-light);
        }

        .metric-card.emergency {
            border-left-color: var(--error-red);
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            animation: emergency-pulse 2s infinite;
        }

        .metric-card.emergency::before {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(239, 68, 68, 0.1) 100%);
        }

        .metric-card.success {
            border-left-color: var(--success-green);
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        }

        .metric-card.success::before {
            background: linear-gradient(135deg, rgba(5, 150, 105, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
        }

        .metric-card.warning {
            border-left-color: var(--warning-orange);
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        }

        .metric-card.warning::before {
            background: linear-gradient(135deg, rgba(217, 119, 6, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
        }

        @keyframes emergency-pulse {
            0% { box-shadow: 0 4px 20px rgba(220, 38, 38, 0.3), 0 0 0 0 rgba(220, 38, 38, 0.7); }
            50% { box-shadow: 0 4px 20px rgba(220, 38, 38, 0.6), 0 0 0 10px rgba(220, 38, 38, 0); }
            100% { box-shadow: 0 4px 20px rgba(220, 38, 38, 0.3), 0 0 0 0 rgba(220, 38, 38, 0); }
        }

        .chart-container {
            background: linear-gradient(135deg, white 0%, var(--neutral-gray-50) 100%);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            margin: 20px 0;
            border: 1px solid var(--neutral-gray-200);
            position: relative;
            overflow: hidden;
        }

        .chart-container::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 150px;
            height: 150px;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.03) 0%, rgba(13, 148, 136, 0.03) 100%);
            border-radius: 50%;
            transform: translate(50px, -50px);
        }

        .activity-item {
            background: linear-gradient(135deg, var(--neutral-gray-50) 0%, white 100%);
            padding: 18px;
            border-radius: 12px;
            margin: 10px 0;
            border-left: 5px solid var(--success-green);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid var(--neutral-gray-200);
            position: relative;
        }

        .activity-item:hover {
            background: linear-gradient(135deg, var(--neutral-gray-100) 0%, var(--neutral-gray-50) 100%);
            transform: translateX(8px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }

        .appointment-item {
            background: linear-gradient(135deg, white 0%, var(--neutral-gray-50) 100%);
            padding: 18px;
            border-radius: 12px;
            margin: 10px 0;
            border: 2px solid var(--neutral-gray-200);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }

        .appointment-item:hover {
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
            transform: translateY(-3px);
            border-color: var(--primary-blue-light);
        }

        .status-badge {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .status-completed {
            background: linear-gradient(135deg, var(--success-green-light) 0%, var(--success-green) 100%);
            color: white;
        }
        .status-progress {
            background: linear-gradient(135deg, var(--warning-orange-light) 0%, var(--warning-orange) 100%);
            color: white;
        }
        .status-emergency {
            background: linear-gradient(135deg, var(--error-red-light) 0%, var(--error-red) 100%);
            color: white;
            animation: status-pulse 1.5s infinite;
        }
        .status-scheduled {
            background: linear-gradient(135deg, var(--primary-blue-light) 0%, var(--primary-blue) 100%);
            color: white;
        }

        @keyframes status-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .metric-value {
            font-size: 2.8em;
            font-weight: 700;
            color: var(--neutral-gray-800);
            margin: 12px 0;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .metric-label {
            font-size: 0.95em;
            color: var(--neutral-gray-600);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .trend-indicator {
            font-size: 0.85em;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 12px;
            margin-top: 8px;
            display: inline-block;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .trend-positive {
            background: linear-gradient(135deg, var(--success-green-light) 0%, var(--success-green) 100%);
            color: white;
        }
        .trend-negative {
            background: linear-gradient(135deg, var(--error-red-light) 0%, var(--error-red) 100%);
            color: white;
        }
        .trend-neutral {
            background: linear-gradient(135deg, var(--neutral-gray-300) 0%, var(--neutral-gray-400) 100%);
            color: white;
        }

        .sidebar-nav {
            background: linear-gradient(135deg, var(--neutral-gray-50) 0%, white 100%);
            padding: 24px;
            border-radius: 16px;
            margin-bottom: 24px;
            border: 1px solid var(--neutral-gray-200);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        }

        .nav-item {
            padding: 12px 18px;
            margin: 6px 0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            font-weight: 500;
            border: 1px solid transparent;
        }

        .nav-item:hover {
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
            transform: translateX(4px);
            border-color: var(--primary-blue-light);
        }

        .nav-item.active {
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-light) 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }

        .emergency-alert {
            background: linear-gradient(135deg, var(--error-red) 0%, var(--error-red-light) 100%);
            color: white;
            padding: 24px;
            border-radius: 16px;
            margin: 18px 0;
            animation: emergency-pulse 1.8s infinite;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(220, 38, 38, 0.3);
        }

        .emergency-alert::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100px;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
            border-radius: 50%;
            transform: translate(30px, -30px);
        }

        @keyframes emergency-pulse {
            0% { box-shadow: 0 0 20px rgba(220, 38, 38, 0.4), 0 0 40px rgba(220, 38, 38, 0.2); }
            50% { box-shadow: 0 0 30px rgba(220, 38, 38, 0.8), 0 0 60px rgba(220, 38, 38, 0.4); }
            100% { box-shadow: 0 0 20px rgba(220, 38, 38, 0.4), 0 0 40px rgba(220, 38, 38, 0.2); }
        }

        .insight-card {
            background: linear-gradient(135deg, white 0%, var(--neutral-gray-50) 100%);
            padding: 24px;
            border-radius: 14px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            margin: 10px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid var(--neutral-gray-200);
            position: relative;
            overflow: hidden;
        }

        .insight-card::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(13, 148, 136, 0.05) 100%);
            border-radius: 50%;
            transform: translate(30px, -30px);
        }

        .insight-card:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        }

        .insight-icon {
            font-size: 2.2em;
            margin-bottom: 12px;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
        }

        .insight-value {
            font-size: 2em;
            font-weight: 700;
            margin: 8px 0;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .insight-label {
            font-size: 0.9em;
            color: var(--neutral-gray-600);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            font-weight: 600;
        }

        /* Enhanced Responsive Design */
        @media (max-width: 768px) {
            .metric-card, .chart-container, .insight-card {
                margin: 12px 0;
                padding: 18px;
            }
            .main-header {
                padding: 20px;
                margin-bottom: 24px;
            }
            .metric-value {
                font-size: 2.2em;
            }
            .insight-value {
                font-size: 1.6em;
            }
        }

        /* Enhanced Loading Animation */
        .loading-spinner {
            border: 5px solid var(--neutral-gray-200);
            border-top: 5px solid var(--primary-blue);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 24px auto;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Enhanced Notification Styles */
        .notification {
            padding: 16px 20px;
            border-radius: 12px;
            margin: 10px 0;
            border-left: 4px solid;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            font-weight: 500;
            position: relative;
            overflow: hidden;
        }

        .notification::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100px;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
            border-radius: 50%;
            transform: translate(30px, -30px);
        }

        .notification.success {
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border-left-color: var(--success-green);
            color: var(--neutral-gray-800);
        }
        .notification.warning {
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
            border-left-color: var(--warning-orange);
            color: var(--neutral-gray-800);
        }
        .notification.error {
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            border-left-color: var(--error-red);
            color: var(--neutral-gray-800);
        }
        .notification.info {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border-left-color: var(--primary-blue);
            color: var(--neutral-gray-800);
        }

        /* Enhanced Button Styles */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-light) 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.95em;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
            background: linear-gradient(135deg, var(--primary-blue-dark) 0%, var(--primary-blue) 100%);
        }

        .stButton > button:active {
            transform: translateY(0);
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
        }

        /* Emergency Button Special Styling */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--error-red) 0%, var(--error-red-light) 100%);
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
            animation: button-pulse 2s infinite;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #b91c1c 0%, var(--error-red) 100%);
            box-shadow: 0 6px 20px rgba(220, 38, 38, 0.4);
        }

        @keyframes button-pulse {
            0%, 100% { box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3); }
            50% { box-shadow: 0 4px 12px rgba(220, 38, 38, 0.5), 0 0 0 0 rgba(220, 38, 38, 0.7); }
        }

        /* Enhanced Sidebar Styling */
        .css-1d391kg { /* Sidebar container */
            background: linear-gradient(180deg, var(--neutral-gray-50) 0%, white 100%);
            border-right: 1px solid var(--neutral-gray-200);
        }

        .css-1d391kg .css-1lcbmhc { /* Sidebar content */
            background: transparent;
        }

        /* Enhanced Header Styling */
        .css-18e3th9 { /* Main content header */
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--accent-purple) 50%, var(--secondary-teal) 100%);
            color: white;
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(37, 99, 235, 0.2);
        }

        /* Current Metrics Sidebar Styling */
        .metrics-sidebar {
            background: linear-gradient(180deg, var(--neutral-gray-50) 0%, white 100%);
            border-radius: 16px;
            padding: 20px;
            margin-left: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid var(--neutral-gray-200);
            position: sticky;
            top: 20px;
            max-height: calc(100vh - 40px);
            overflow-y: auto;
        }

        .metrics-sidebar::-webkit-scrollbar {
            width: 6px;
        }

        .metrics-sidebar::-webkit-scrollbar-track {
            background: var(--neutral-gray-100);
            border-radius: 3px;
        }

        .metrics-sidebar::-webkit-scrollbar-thumb {
            background: var(--primary-blue-light);
            border-radius: 3px;
        }

        .metrics-sidebar::-webkit-scrollbar-thumb:hover {
            background: var(--primary-blue);
        }

        .metrics-header {
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-light) 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 4px 16px rgba(37, 99, 235, 0.2);
        }

        .metrics-header h3 {
            margin: 0;
            font-size: 1.3em;
            font-weight: 700;
        }

        .metrics-header p {
            margin: 8px 0 0 0;
            opacity: 0.9;
            font-size: 0.85em;
        }

        .metrics-section {
            margin-bottom: 24px;
        }

        .metrics-section h4 {
            color: var(--neutral-gray-800);
            font-size: 1em;
            font-weight: 600;
            margin-bottom: 12px;
            border-bottom: 2px solid var(--primary-blue-light);
            padding-bottom: 4px;
        }

        .metrics-item {
            background: white;
            padding: 12px 16px;
            border-radius: 10px;
            margin: 6px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            border: 1px solid var(--neutral-gray-200);
            transition: all 0.3s ease;
        }

        .metrics-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }

        .alert-item {
            background: rgba(255, 255, 255, 0.95);
            padding: 10px 14px;
            border-radius: 8px;
            margin: 6px 0;
            font-size: 0.85em;
            border-left: 4px solid;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        }

        .alert-critical { border-left-color: var(--error-red); }
        .alert-warning { border-left-color: var(--warning-orange); }
        .alert-info { border-left-color: var(--primary-blue); }
        .alert-success { border-left-color: var(--success-green); }

        .health-indicator {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 14px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 8px;
            margin: 6px 0;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        }

        .health-indicator .status {
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }

        .status-healthy {
            background: linear-gradient(135deg, var(--success-green-light) 0%, var(--success-green) 100%);
            color: white;
        }

        .status-degraded {
            background: linear-gradient(135deg, var(--warning-orange-light) 0%, var(--warning-orange) 100%);
            color: white;
        }

        .status-critical {
            background: linear-gradient(135deg, var(--error-red-light) 0%, var(--error-red) 100%);
            color: white;
        }

        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def create_metric_card(title: str, value: str, subtitle: str = "", trend: str = "", card_type: str = "default"):
        """Create a metric card component"""
        card_class = f"metric-card {card_type}"

        trend_html = ""
        if trend:
            trend_class = "trend-positive" if trend.startswith("+") else "trend-negative" if trend.startswith("-") else "trend-neutral"
            trend_html = f'<div class="trend-indicator {trend_class}">{trend}</div>'

        html = f"""
        <div class="{card_class}">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            {f'<div style="color: #6c757d; font-size: 0.9em;">{subtitle}</div>' if subtitle else ''}
            {trend_html}
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def create_activity_item(patient: str, time: str, status: str, activity_type: str, doctor: str = ""):
        """Create an activity item component"""
        status_class = {
            "Completed": "status-completed",
            "In Progress": "status-progress",
            "Emergency": "status-emergency",
            "Scheduled": "status-scheduled"
        }.get(status, "status-completed")

        doctor_info = f" • {doctor}" if doctor else ""

        html = f"""
        <div class="activity-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{patient}</strong><br>
                    <small style="color: #6c757d;">{time}{doctor_info} • {activity_type}</small>
                </div>
                <span class="status-badge {status_class}">{status}</span>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def create_appointment_item(time: str, patient: str, appointment_type: str, doctor: str = ""):
        """Create an appointment item component"""
        doctor_info = f"<br><small style='color: #6c757d;'>with {doctor}</small>" if doctor else ""

        html = f"""
        <div class="appointment-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{time}</strong> - {patient}<br>
                    <small style="color: #6c757d;">{appointment_type}</small>{doctor_info}
                </div>
                <button style="background: #4A90E2; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.9em; transition: all 0.2s ease;" onmouseover="this.style.background='#357ABD'" onmouseout="this.style.background='#4A90E2'">Join Call</button>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def create_insight_card(icon: str, value: str, label: str, color: str = "#4A90E2"):
        """Create an insight card component"""
        html = f"""
        <div class="insight-card" style="border-left: 4px solid {color};">
            <div class="insight-icon">{icon}</div>
            <div class="insight-value" style="color: {color};">{value}</div>
            <div class="insight-label">{label}</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def create_emergency_alert(patient: str, condition: str, time: str, severity: str, action: str):
        """Create an emergency alert component"""
        severity_colors = {
            "Critical": "#E74C3C",
            "High": "#F39C12",
            "Medium": "#F1C40F",
            "Low": "#28a745"
        }
        color = severity_colors.get(severity, "#E74C3C")

        html = f"""
        <div class="emergency-alert">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; color: white;">🚨 Emergency Alert</h4>
                <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 12px; font-size: 0.8em;">{severity}</span>
            </div>
            <div style="margin-bottom: 8px;">
                <strong style="color: white;">Patient: {patient}</strong>
            </div>
            <div style="margin-bottom: 8px; color: #FFE4E1;">
                {condition} • {time}
            </div>
            <div style="color: #FFE4E1; font-style: italic;">
                {action}
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def create_notification(message: str, type: str = "info"):
        """Create a notification component"""
        html = f"""
        <div class="notification {type}">
            {message}
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def show_loading_spinner():
        """Show a loading spinner"""
        html = '<div class="loading-spinner"></div>'
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def create_sidebar_nav(options: List[str], active_option: str):
        """Create sidebar navigation"""
        st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
        st.markdown("### 🧭 Navigation")

        for option in options:
            is_active = option == active_option
            active_class = "active" if is_active else ""
            st.markdown(f'<div class="nav-item {active_class}">{option}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# Global UI components instance
ui = UIComponents()
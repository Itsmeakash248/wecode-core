"""
BioSync Tele-Rescue - Data Management Module
Handles mock data generation and management for the healthcare dashboard
"""

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any


class DataManager:
    """Central data management for the healthcare dashboard"""

    def __init__(self):
        self.doctors = self._generate_doctors()
        self.patients = self._generate_patients()
        self.appointments = self._generate_appointments()

    def _generate_doctors(self) -> List[Dict[str, Any]]:
        """Generate mock doctor data"""
        doctors_data = [
            {"id": 1, "name": "Dr. Sarah Johnson", "specialty": "Cardiology", "status": "Available", "rating": 4.9, "experience": 12},
            {"id": 2, "name": "Dr. Michael Chen", "specialty": "Emergency Medicine", "status": "Available", "rating": 4.8, "experience": 15},
            {"id": 3, "name": "Dr. Emily Rodriguez", "specialty": "Neurology", "status": "Busy", "rating": 4.7, "experience": 10},
            {"id": 4, "name": "Dr. David Kim", "specialty": "Pediatrics", "status": "Available", "rating": 4.9, "experience": 8},
            {"id": 5, "name": "Dr. Lisa Thompson", "specialty": "Internal Medicine", "status": "Offline", "rating": 4.6, "experience": 20},
        ]
        return doctors_data

    def _generate_patients(self) -> List[Dict[str, Any]]:
        """Generate mock patient data"""
        patients_data = [
            {"id": 1, "name": "John Doe", "age": 45, "condition": "Hypertension", "last_visit": "2024-01-15", "risk_level": "Medium"},
            {"id": 2, "name": "Sarah Wilson", "age": 32, "condition": "Cardiac Arrhythmia", "last_visit": "2024-01-14", "risk_level": "High"},
            {"id": 3, "name": "Mike Johnson", "age": 58, "condition": "Diabetes", "last_visit": "2024-01-13", "risk_level": "Medium"},
            {"id": 4, "name": "Emma Davis", "age": 29, "condition": "Anxiety", "last_visit": "2024-01-12", "risk_level": "Low"},
            {"id": 5, "name": "Robert Brown", "age": 67, "condition": "COPD", "last_visit": "2024-01-11", "risk_level": "High"},
        ]
        return patients_data

    def _generate_appointments(self) -> List[Dict[str, Any]]:
        """Generate mock appointment data"""
        appointments_data = [
            {"id": 1, "patient_id": 1, "doctor_id": 1, "time": "09:00 AM", "date": "2024-01-15", "type": "Follow-up", "status": "Scheduled"},
            {"id": 2, "patient_id": 2, "doctor_id": 2, "time": "10:30 AM", "date": "2024-01-15", "type": "Emergency", "status": "In Progress"},
            {"id": 3, "patient_id": 3, "doctor_id": 1, "time": "02:00 PM", "date": "2024-01-15", "type": "Consultation", "status": "Scheduled"},
            {"id": 4, "patient_id": 4, "doctor_id": 4, "time": "03:30 PM", "date": "2024-01-15", "type": "Therapy", "status": "Scheduled"},
        ]
        return appointments_data

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get dashboard overview metrics"""
        return {
            'total_consultations': random.randint(1200, 1300),
            'active_patients': random.randint(85, 95),
            'emergency_cases': random.randint(8, 15),
            'today_appointments': random.randint(6, 10),
            'available_doctors': len([d for d in self.doctors if d['status'] == 'Available']),
            'total_doctors': len(self.doctors)
        }

    def get_doctor_listing(self, status_filter: str = "All") -> List[Dict[str, Any]]:
        """Get doctor listing optionally filtered by availability status."""
        if status_filter == "All":
            status_order = {"Available": 0, "Busy": 1, "Offline": 2}
            return sorted(self.doctors, key=lambda d: (status_order.get(d['status'], 99), d['name']))
        return [doctor for doctor in self.doctors if doctor['status'] == status_filter]

    def get_doctor_availability_counts(self) -> Dict[str, int]:
        """Get doctor count summary for each availability state."""
        return {
            'available': len([doctor for doctor in self.doctors if doctor['status'] == 'Available']),
            'busy': len([doctor for doctor in self.doctors if doctor['status'] == 'Busy']),
            'offline': len([doctor for doctor in self.doctors if doctor['status'] == 'Offline']),
            'total': len(self.doctors)
        }

    def get_vitals_data(self) -> Dict[str, Any]:
        """Generate real-time vitals data"""
        return {
            'Heart Rate': random.randint(60, 100),
            'SpO2': random.randint(95, 100),
            'Temperature': round(random.uniform(36.5, 37.5), 1),
            'Blood Pressure': f"{random.randint(110, 130)}/{random.randint(70, 90)}",
            'Respiratory Rate': random.randint(12, 20),
            'Blood Glucose': random.randint(70, 140)
        }

    def get_consultation_trends(self, days: int = 30) -> pd.DataFrame:
        """Generate consultation trends data"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=days-1), periods=days, freq='D')
        consultations = [random.randint(5, 25) for _ in range(days)]
        return pd.DataFrame({'Date': dates, 'Consultations': consultations})

    def get_patient_categories(self) -> Dict[str, int]:
        """Get patient distribution by category"""
        return {
            'Cardiology': random.randint(30, 40),
            'Emergency': random.randint(20, 30),
            'General Medicine': random.randint(15, 25),
            'Neurology': random.randint(10, 20),
            'Pediatrics': random.randint(8, 15),
            'Mental Health': random.randint(5, 12)
        }

    def get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent consultation activity"""
        activities = [
            {"patient": "John Doe", "time": "10:30 AM", "status": "Completed", "type": "Regular Checkup", "doctor": "Dr. Sarah Johnson"},
            {"patient": "Sarah Wilson", "time": "09:45 AM", "status": "In Progress", "type": "Emergency", "doctor": "Dr. Michael Chen"},
            {"patient": "Mike Johnson", "time": "09:15 AM", "status": "Completed", "type": "Follow-up", "doctor": "Dr. Sarah Johnson"},
            {"patient": "Emma Davis", "time": "08:30 AM", "status": "Completed", "type": "Consultation", "doctor": "Dr. David Kim"},
            {"patient": "Robert Brown", "time": "08:00 AM", "status": "Completed", "type": "Regular Checkup", "doctor": "Dr. Lisa Thompson"},
        ]
        return activities

    def get_upcoming_appointments(self) -> List[Dict[str, Any]]:
        """Get upcoming appointments"""
        appointments = [
            {"time": "11:00 AM", "patient": "Alice Cooper", "type": "Cardiology Review", "doctor": "Dr. Sarah Johnson"},
            {"time": "11:30 AM", "patient": "Bob Wilson", "type": "Follow-up", "doctor": "Dr. Michael Chen"},
            {"time": "02:00 PM", "patient": "Carol Smith", "type": "Consultation", "doctor": "Dr. Emily Rodriguez"},
            {"time": "03:30 PM", "patient": "David Johnson", "type": "Emergency Review", "doctor": "Dr. Sarah Johnson"},
        ]
        return appointments

    def get_emergency_alerts(self) -> List[Dict[str, Any]]:
        """Get active emergency alerts"""
        alerts = [
            {
                "patient": "Sarah Wilson",
                "condition": "Cardiac arrest detected",
                "time": "2 min ago",
                "severity": "Critical",
                "action": "Auto-dialing emergency doctor"
            },
            {
                "patient": "Mike Johnson",
                "condition": "Severe chest pain",
                "time": "5 min ago",
                "severity": "High",
                "action": "Immediate consultation initiated"
            }
        ]
        return alerts

    def get_patient_insights(self) -> List[Dict[str, Any]]:
        """Get patient health insights"""
        return [
            {"metric": "Average Heart Rate", "value": "87%", "icon": "💓", "trend": "+2%", "color": "#28a745"},
            {"metric": "Average SpO2", "value": "96%", "icon": "🫁", "trend": "+1%", "color": "#4A90E2"},
            {"metric": "Average Temperature", "value": "36.8°C", "icon": "🌡️", "trend": "0%", "color": "#F39C12"},
            {"metric": "Critical Alerts", "value": "23", "icon": "⚡", "trend": "-5%", "color": "#E74C3C"},
        ]

    def search_patients(self, query: str) -> List[Dict[str, Any]]:
        """Search patients by name or condition"""
        query = query.lower()
        return [p for p in self.patients if query in p['name'].lower() or query in p['condition'].lower()]

    def get_doctor_schedule(self, doctor_id: int) -> List[Dict[str, Any]]:
        """Get doctor's schedule for today"""
        # Mock schedule data
        return [
            {"time": "09:00", "patient": "John Doe", "type": "Checkup"},
            {"time": "10:00", "patient": "Available", "type": "Free"},
            {"time": "11:00", "patient": "Sarah Wilson", "type": "Emergency"},
            {"time": "12:00", "patient": "Lunch Break", "type": "Break"},
            {"time": "13:00", "patient": "Mike Johnson", "type": "Consultation"},
            {"time": "14:00", "patient": "Available", "type": "Free"},
            {"time": "15:00", "patient": "Emma Davis", "type": "Follow-up"},
        ]

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics for the metrics sidebar"""
        return {
            'server_load': random.randint(15, 85),
            'memory_usage': random.randint(40, 90),
            'cpu_usage': random.randint(20, 80),
            'disk_usage': random.randint(30, 70),
            'response_time': random.randint(50, 200),
            'uptime': round(random.uniform(99.5, 99.9), 1),
            'error_rate': round(random.uniform(0.01, 0.5), 1),
            'throughput': random.randint(50, 200),
            'emergency_status': {
                'active_alerts': random.randint(0, 5),
                'critical_cases': random.randint(0, 3),
                'available_staff': random.randint(8, 15)
            },
            'network': {
                'bandwidth': random.randint(50, 95),
                'connections': random.randint(100, 500),
                'latency': random.randint(5, 50),
                'packet_loss': round(random.uniform(0.01, 0.1), 1)
            },
            'recent_alerts': [
                {'type': 'critical', 'message': 'Patient vitals abnormal - 2 min ago'},
                {'type': 'warning', 'message': 'High server load detected - 5 min ago'},
                {'type': 'info', 'message': 'Backup completed successfully - 12 min ago'},
                {'type': 'critical', 'message': 'Emergency call failed - 18 min ago'}
            ],
            'health_indicators': [
                {'component': 'Database', 'status': random.choice(['healthy', 'healthy', 'healthy', 'degraded'])},
                {'component': 'API Services', 'status': random.choice(['healthy', 'healthy', 'healthy', 'degraded'])},
                {'component': 'Video Streaming', 'status': random.choice(['healthy', 'degraded', 'critical'])},
                {'component': 'Emergency System', 'status': 'healthy'}
            ],
            'quick_stats': {
                'total_patients': random.randint(150, 200),
                'active_sessions': random.randint(15, 30),
                'completed_consults': random.randint(80, 120),
                'avg_wait_time': random.randint(5, 15)
            }
        }


# Global data manager instance
data_manager = DataManager()
"""
API-backed Streamlit views for the core telemedicine features.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from .data_manager import data_manager
from .platform_api import (
    ApiError,
    BackendUnavailable,
    book_appointment,
    feedback_summary,
    health,
    list_appointments,
    list_doctors,
    list_feedback,
    list_notifications,
    list_patients,
    mark_notification_read,
    process_reminders,
    submit_feedback,
    update_appointment,
    update_doctor_status,
)
from .ui_components import ui
from .webrtc_consultation import consultation_module


LOCAL_TZ = datetime.now().astimezone().tzinfo or timezone.utc
STATUS_LABELS = {
    "confirmed": "Confirmed",
    "in_progress": "In Progress",
    "completed": "Completed",
    "cancelled": "Cancelled",
    "available": "Available",
    "busy": "Busy",
    "offline": "Offline",
}
STATUS_COLORS = {
    "confirmed": "#2563eb",
    "in_progress": "#d97706",
    "completed": "#059669",
    "cancelled": "#6b7280",
}
NOTIFICATION_TONES = {
    "appointment": "info",
    "reminder": "warning",
    "feedback": "success",
    "sos": "error",
}


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(LOCAL_TZ)


def _format_datetime(value: Optional[str]) -> str:
    parsed = _parse_iso(value)
    if parsed is None:
        return "Not scheduled"
    return parsed.strftime("%b %d, %Y %I:%M %p")


def _status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status.replace("_", " ").title())


def _combine_to_iso(date_value, time_value) -> str:
    combined = datetime.combine(date_value, time_value)
    combined = combined.replace(tzinfo=LOCAL_TZ)
    return combined.astimezone(timezone.utc).isoformat()


def _set_flash(message: str, tone: str = "success") -> None:
    st.session_state.platform_flash = {"message": message, "tone": tone}


def _render_flash() -> None:
    payload = st.session_state.pop("platform_flash", None)
    if payload:
        ui.create_notification(payload["message"], payload["tone"])


def _with_api_error(action):
    try:
        return action()
    except BackendUnavailable as exc:
        st.error(str(exc))
        st.caption("Use `start.sh` to run the backend and Streamlit together.")
        return None
    except ApiError as exc:
        st.error(str(exc))
        return None


def _ensure_backend() -> bool:
    result = _with_api_error(health)
    if not result:
        return False
    return True


def _render_notification_list(uid: str, title: str, key_prefix: str) -> None:
    st.markdown(f"### {title}")
    cols = st.columns([1, 1, 2])
    with cols[0]:
        unread_only = st.checkbox("Unread only", key=f"{key_prefix}_unread_only")
    with cols[1]:
        if st.button("Refresh reminders", key=f"{key_prefix}_reminders"):
            result = _with_api_error(process_reminders)
            if result is not None:
                _set_flash(f"Reminder scan complete. Generated {result['generated']} reminder(s).", "info")
                st.rerun()

    notifications = _with_api_error(lambda: list_notifications(uid, unread_only=unread_only))
    if notifications is None:
        return

    unread_count = len([item for item in notifications if not item["read"]])
    st.caption(f"{unread_count} unread notification(s)")

    if not notifications:
        st.info("No notifications yet.")
        return

    for notification in notifications:
        tone = NOTIFICATION_TONES.get(notification["type"], "info")
        label = "Unread" if not notification["read"] else "Read"
        columns = st.columns([6, 1])
        with columns[0]:
            ui.create_notification(
                f"{notification['message']}<br><small>{_format_datetime(notification['created_at'])} • {notification['type'].title()} • {label}</small>",
                tone,
            )
        with columns[1]:
            if not notification["read"] and st.button("Read", key=f"{key_prefix}_read_{notification['notification_id']}"):
                result = _with_api_error(lambda: mark_notification_read(uid, notification["notification_id"]))
                if result is not None:
                    st.rerun()


def _appointment_metrics(appointments: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "total": len(appointments),
        "confirmed": len([item for item in appointments if item["status"] == "confirmed"]),
        "live": len([item for item in appointments if item["status"] == "in_progress"]),
        "completed": len([item for item in appointments if item["status"] == "completed"]),
        "cancelled": len([item for item in appointments if item["status"] == "cancelled"]),
    }


def _render_doctor_cards(doctors: list[dict[str, Any]], title: str) -> None:
    st.markdown(f"### {title}")
    if not doctors:
        st.info("No doctors found.")
        return

    for doctor in doctors:
        ui.create_doctor_availability_item(
            name=doctor["name"],
            specialty=doctor["specialty"],
            status=_status_label(doctor["status"]),
            rating=doctor["rating"],
            experience=doctor.get("experience", 0),
        )


def _render_patient_booking(patient: dict[str, Any], doctors: list[dict[str, Any]]) -> None:
    st.markdown("### Book Appointment")
    available_doctors = [doctor for doctor in doctors if doctor["status"] == "available"]
    if not available_doctors:
        st.warning("No doctors are currently available for new appointments.")
        return

    doctor_map = {doctor["id"]: doctor for doctor in available_doctors}
    default_time = datetime.now().astimezone() + timedelta(minutes=20)

    emergency_col, booking_col = st.columns([1, 3])
    with emergency_col:
        if st.button("Emergency SOS", key=f"patient_emergency_{patient['id']}", type="primary"):
            emergency_doctor = available_doctors[0]
            payload = {
                "patient_name": patient["name"],
                "patient_id": patient["id"],
                "doctor_id": emergency_doctor["id"],
                "symptoms": f"Emergency escalation for {patient['condition']}.",
                "scheduled_time": datetime.now(timezone.utc).isoformat(),
                "consultation_type": "Emergency",
            }
            appointment = _with_api_error(lambda: book_appointment(payload))
            if appointment is not None:
                st.session_state.patient_active_appointment_id = appointment["appointment_id"]
                st.session_state.patient_active_room = appointment["consultation_room_id"]
                st.session_state.consultation_room_input_patient = appointment["consultation_room_id"]
                _set_flash(
                    f"Emergency consultation created with {appointment['doctor_name']}. Join room {appointment['consultation_room_id']}.",
                    "warning",
                )
                st.rerun()

    with booking_col:
        with st.form(f"book_appointment_{patient['id']}"):
            doctor_id = st.selectbox(
                "Doctor",
                options=list(doctor_map.keys()),
                format_func=lambda item: f"{doctor_map[item]['name']} • {doctor_map[item]['specialty']} • ⭐ {doctor_map[item]['rating']}",
            )
            consultation_type = st.selectbox(
                "Consultation Type",
                ["Consultation", "Follow-up", "Emergency", "Screening"],
            )
            schedule_col1, schedule_col2 = st.columns(2)
            with schedule_col1:
                appointment_date = st.date_input("Appointment Date", value=default_time.date())
            with schedule_col2:
                appointment_time = st.time_input("Appointment Time", value=default_time.time().replace(second=0, microsecond=0))
            symptoms = st.text_area("Symptoms / Reason", placeholder="Describe the patient's issue in one or two sentences.")
            submitted = st.form_submit_button("Book Appointment")

            if submitted:
                if not symptoms.strip():
                    st.warning("Add symptoms before booking the appointment.")
                else:
                    payload = {
                        "patient_name": patient["name"],
                        "patient_id": patient["id"],
                        "doctor_id": doctor_id,
                        "symptoms": symptoms.strip(),
                        "scheduled_time": _combine_to_iso(appointment_date, appointment_time),
                        "consultation_type": consultation_type,
                    }
                    appointment = _with_api_error(lambda: book_appointment(payload))
                    if appointment is not None:
                        _set_flash(
                            f"Appointment {appointment['appointment_id']} booked with {appointment['doctor_name']} for {_format_datetime(appointment['scheduled_time'])}.",
                            "success",
                        )
                        st.rerun()


def _render_patient_appointments(patient: dict[str, Any], appointments: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    st.markdown("### My Appointments")
    if not appointments:
        st.info("No appointments booked yet.")
        return None

    active_appointment = None
    appointment_map = {item["appointment_id"]: item for item in appointments}
    selected_id = st.session_state.get("patient_active_appointment_id")
    if selected_id in appointment_map:
        active_appointment = appointment_map[selected_id]
    else:
        active_appointment = next((item for item in appointments if item["status"] == "in_progress"), None)

    metrics = _appointment_metrics(appointments)
    metric_cols = st.columns(4)
    metric_cols[0].metric("Total", metrics["total"])
    metric_cols[1].metric("Confirmed", metrics["confirmed"])
    metric_cols[2].metric("Live", metrics["live"])
    metric_cols[3].metric("Completed", metrics["completed"])

    for appointment in appointments:
        label = (
            f"{_format_datetime(appointment['scheduled_time'])} • "
            f"{appointment['doctor_name']} • {_status_label(appointment['status'])}"
        )
        with st.expander(label, expanded=appointment["status"] == "in_progress"):
            st.markdown(f"**Appointment ID:** `{appointment['appointment_id']}`")
            st.markdown(f"**Consultation Type:** {appointment['consultation_type']}")
            st.markdown(f"**Symptoms:** {appointment['symptoms']}")
            st.markdown(f"**Room ID:** `{appointment['consultation_room_id']}`")

            action_cols = st.columns(3)
            with action_cols[0]:
                if appointment["status"] in {"confirmed", "in_progress"} and st.button(
                    "Join Consultation",
                    key=f"patient_join_{appointment['appointment_id']}",
                ):
                    if appointment["status"] == "confirmed":
                        result = _with_api_error(
                            lambda: update_appointment(appointment["appointment_id"], {"status": "in_progress"})
                        )
                        if result is None:
                            return active_appointment
                    st.session_state.patient_active_appointment_id = appointment["appointment_id"]
                    st.session_state.patient_active_room = appointment["consultation_room_id"]
                    st.session_state.consultation_room_input_patient = appointment["consultation_room_id"]
                    _set_flash(f"Joined consultation room {appointment['consultation_room_id']}.", "info")
                    st.rerun()
            with action_cols[1]:
                if appointment["status"] == "confirmed" and st.button(
                    "Cancel Appointment",
                    key=f"patient_cancel_{appointment['appointment_id']}",
                ):
                    result = _with_api_error(
                        lambda: update_appointment(appointment["appointment_id"], {"status": "cancelled"})
                    )
                    if result is not None:
                        _set_flash(f"Appointment {appointment['appointment_id']} cancelled.", "warning")
                        st.rerun()
            with action_cols[2]:
                st.caption(f"Last updated: {_format_datetime(appointment['updated_at'])}")

    return active_appointment


def _render_patient_feedback(patient: dict[str, Any], appointments: list[dict[str, Any]]) -> None:
    st.markdown("### Patient Feedback")
    feedback_entries = _with_api_error(lambda: list_feedback(patient_id=patient["id"]))
    if feedback_entries is None:
        return

    completed_appointments = [item for item in appointments if item["status"] == "completed"]
    feedback_by_appointment = {item["appointment_id"] for item in feedback_entries}
    eligible = [item for item in completed_appointments if item["appointment_id"] not in feedback_by_appointment]

    if eligible:
        appointment_map = {item["appointment_id"]: item for item in eligible}
        with st.form(f"feedback_form_{patient['id']}"):
            appointment_id = st.selectbox(
                "Completed Appointment",
                options=list(appointment_map.keys()),
                format_func=lambda item: (
                    f"{item} • {appointment_map[item]['doctor_name']} • "
                    f"{_format_datetime(appointment_map[item]['scheduled_time'])}"
                ),
            )
            rating_col1, rating_col2, rating_col3 = st.columns(3)
            with rating_col1:
                rating = st.slider("Overall Rating", 1, 5, 5)
            with rating_col2:
                communication = st.slider("Communication", 1, 5, 5)
            with rating_col3:
                wait_time = st.slider("Wait Time", 1, 5, 4)
            recommend = st.checkbox("I would recommend this doctor", value=True)
            comment = st.text_area("Comment", placeholder="What worked well? What can improve?")
            submitted = st.form_submit_button("Submit Feedback")

            if submitted:
                if not comment.strip():
                    st.warning("Add a short comment before submitting feedback.")
                else:
                    appointment = appointment_map[appointment_id]
                    payload = {
                        "patient_id": patient["id"],
                        "doctor_id": appointment["doctor_id"],
                        "appointment_id": appointment_id,
                        "rating": rating,
                        "communication": communication,
                        "wait_time": wait_time,
                        "recommend": recommend,
                        "comment": comment.strip(),
                    }
                    result = _with_api_error(lambda: submit_feedback(payload))
                    if result is not None:
                        _set_flash("Feedback submitted successfully.", "success")
                        st.rerun()
    else:
        st.info("No completed appointments are waiting for feedback.")

    if not feedback_entries:
        st.caption("No feedback submitted yet.")
        return

    summary = _with_api_error(lambda: feedback_summary(patient_id=patient["id"]))
    if summary is not None:
        metric_cols = st.columns(4)
        metric_cols[0].metric("Feedback Count", summary["total_feedback"])
        metric_cols[1].metric("Avg Rating", f"{summary['avg_rating']}/5")
        metric_cols[2].metric("Recommend Rate", f"{summary['recommend_percent']}%")
        metric_cols[3].metric("Low Ratings", summary["low_ratings"])

    st.markdown("#### Previous Feedback")
    for item in feedback_entries[:5]:
        with st.expander(
            f"{item['doctor_name']} • {item['rating']}/5 • {_format_datetime(item['created_at'])}",
            expanded=False,
        ):
            st.markdown(f"**Communication:** {item['communication']}/5")
            st.markdown(f"**Wait Time:** {item['wait_time']}/5")
            st.markdown(f"**Would Recommend:** {'Yes' if item['recommend'] else 'No'}")
            st.markdown(f"**Comment:** {item.get('comment') or 'No comment'}")


def _render_patient_vitals() -> None:
    st.markdown("### Live Patient Snapshot")
    vitals = data_manager.get_vitals_data()
    col1, col2, col3 = st.columns(3)
    with col1:
        ui.create_metric_card("Heart Rate", f"{vitals['Heart Rate']} bpm", "Simulated wearable feed")
    with col2:
        ui.create_metric_card("SpO2", f"{vitals['SpO2']}%", "Current oxygen saturation")
    with col3:
        ui.create_metric_card("Blood Pressure", vitals["Blood Pressure"], "Latest reading")


def render_patient_dashboard(auth_user: Optional[dict[str, Any]] = None) -> None:
    ui.inject_global_css()
    st.markdown("## Patient Teleconsultation Workspace")
    _render_flash()

    if not _ensure_backend():
        return

    patients = _with_api_error(list_patients)
    doctors = _with_api_error(list_doctors)
    if patients is None or doctors is None:
        return

    patient_map = {patient["id"]: patient for patient in patients}
    if auth_user is not None:
        selected_patient_id = auth_user["linked_profile_id"]
        patient = patient_map.get(selected_patient_id)
        if patient is None:
            st.error("The signed-in patient profile could not be found.")
            return
        st.caption(f"Signed in as {auth_user['full_name']} • {auth_user['email']}")
    else:
        default_patient_id = st.session_state.get("selected_patient_id", patients[0]["id"])
        selected_patient_id = st.selectbox(
            "Patient Profile",
            options=list(patient_map.keys()),
            index=list(patient_map.keys()).index(default_patient_id) if default_patient_id in patient_map else 0,
            format_func=lambda item: f"{patient_map[item]['name']} • {patient_map[item]['condition']} • Risk {patient_map[item]['risk_level']}",
        )
        st.session_state.selected_patient_id = selected_patient_id
        patient = patient_map[selected_patient_id]

    appointments = _with_api_error(lambda: list_appointments(user_id=patient["id"], role="patient"))
    if appointments is None:
        return

    available_doctors = len([doctor for doctor in doctors if doctor["status"] == "available"])
    unread_notifications = _with_api_error(lambda: list_notifications(patient["id"], unread_only=True))
    unread_count = len(unread_notifications or [])

    metrics = _appointment_metrics(appointments)
    top_cols = st.columns(4)
    top_cols[0].metric("Available Doctors", available_doctors)
    top_cols[1].metric("Upcoming", metrics["confirmed"])
    top_cols[2].metric("Live Consultations", metrics["live"])
    top_cols[3].metric("Unread Notifications", unread_count)

    _render_patient_vitals()
    _render_doctor_cards(doctors, "Doctor Listing & Availability")
    _render_patient_booking(patient, doctors)
    active_appointment = _render_patient_appointments(patient, appointments)

    if active_appointment and active_appointment["status"] in {"confirmed", "in_progress"}:
        st.markdown("---")
        st.markdown("### Consultation Room")
        st.caption(
            f"Appointment `{active_appointment['appointment_id']}` • Room `{active_appointment['consultation_room_id']}`"
        )
        st.session_state.consultation_room_input_patient = active_appointment["consultation_room_id"]
        consultation_module.render(
            role="Patient",
            default_room_id=active_appointment["consultation_room_id"],
            section_title=f"Live Consultation with {active_appointment['doctor_name']}",
        )

    st.markdown("---")
    _render_notification_list(patient["id"], "Notifications & Reminders", f"patient_notifications_{patient['id']}")
    st.markdown("---")
    _render_patient_feedback(patient, appointments)


def _render_doctor_status_controls(doctor: dict[str, Any]) -> None:
    st.markdown("### My Availability")
    status_options = ["available", "busy", "offline"]
    selected_status = st.selectbox(
        "Set current status",
        options=status_options,
        index=status_options.index(doctor["status"]),
        format_func=_status_label,
        key=f"doctor_status_{doctor['id']}",
    )
    if st.button("Update Availability", key=f"doctor_status_submit_{doctor['id']}"):
        result = _with_api_error(lambda: update_doctor_status(doctor["id"], selected_status))
        if result is not None:
            _set_flash(f"Availability updated to {_status_label(result['status'])}.", "success")
            st.rerun()


def _render_doctor_dashboard_overview(doctor: dict[str, Any], all_doctors: list[dict[str, Any]], appointments: list[dict[str, Any]]) -> None:
    st.markdown("### Dashboard Overview")
    metrics = _appointment_metrics(appointments)
    feedback = _with_api_error(lambda: feedback_summary(doctor_id=doctor["id"]))
    unread_notifications = _with_api_error(lambda: list_notifications(doctor["id"], unread_only=True))
    unread_count = len(unread_notifications or [])

    top_cols = st.columns(5)
    top_cols[0].metric("Status", _status_label(doctor["status"]))
    top_cols[1].metric("Appointments", metrics["total"])
    top_cols[2].metric("Live", metrics["live"])
    top_cols[3].metric("Unread Alerts", unread_count)
    top_cols[4].metric("Rating", f"{doctor['rating']}/5")

    left_col, right_col = st.columns(2)
    with left_col:
        availability_counts = pd.DataFrame(
            {
                "Status": ["Available", "Busy", "Offline"],
                "Count": [
                    len([item for item in all_doctors if item["status"] == "available"]),
                    len([item for item in all_doctors if item["status"] == "busy"]),
                    len([item for item in all_doctors if item["status"] == "offline"]),
                ],
            }
        )
        fig_status = px.bar(
            availability_counts,
            x="Status",
            y="Count",
            color="Status",
            color_discrete_sequence=["#059669", "#d97706", "#6b7280"],
            title="Doctor Availability",
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with right_col:
        if feedback is None:
            return
        quality_df = pd.DataFrame(
            {
                "Metric": ["Overall", "Communication", "Wait Time"],
                "Score": [
                    feedback["avg_rating"],
                    feedback["avg_communication"],
                    feedback["avg_wait_time"],
                ],
            }
        )
        fig_quality = px.bar(
            quality_df,
            x="Metric",
            y="Score",
            color="Metric",
            color_discrete_sequence=["#2563eb", "#0d9488", "#d97706"],
            title="Feedback Quality Snapshot",
        )
        fig_quality.update_layout(yaxis_range=[0, 5])
        st.plotly_chart(fig_quality, use_container_width=True)

    if appointments:
        timeline_df = pd.DataFrame(
            {
                "Scheduled": [_parse_iso(item["scheduled_time"]) for item in appointments],
                "Status": [_status_label(item["status"]) for item in appointments],
                "Patient": [item["patient_name"] for item in appointments],
            }
        )
        fig_timeline = px.scatter(
            timeline_df,
            x="Scheduled",
            y="Status",
            color="Status",
            hover_data=["Patient"],
            title="Appointment Timeline",
            color_discrete_sequence=["#2563eb", "#d97706", "#059669", "#6b7280"],
        )
        st.plotly_chart(fig_timeline, use_container_width=True)


def _render_doctor_appointments(doctor: dict[str, Any], appointments: list[dict[str, Any]]) -> None:
    st.markdown("### Appointment Management")
    if not appointments:
        st.info("No appointments assigned to this doctor.")
        return

    appointment_map = {item["appointment_id"]: item for item in appointments}
    current_live = next((item for item in appointments if item["status"] == "in_progress"), None)
    if current_live:
        st.session_state.doctor_active_appointment_id = current_live["appointment_id"]
        st.session_state.doctor_active_room = current_live["consultation_room_id"]

    for appointment in appointments:
        title = (
            f"{_format_datetime(appointment['scheduled_time'])} • "
            f"{appointment['patient_name']} • {_status_label(appointment['status'])}"
        )
        with st.expander(title, expanded=appointment["status"] == "in_progress"):
            st.markdown(f"**Appointment ID:** `{appointment['appointment_id']}`")
            st.markdown(f"**Consultation Type:** {appointment['consultation_type']}")
            st.markdown(f"**Symptoms:** {appointment['symptoms']}")
            st.markdown(f"**Room ID:** `{appointment['consultation_room_id']}`")

            button_cols = st.columns(4)
            with button_cols[0]:
                if appointment["status"] in {"confirmed", "in_progress"} and st.button(
                    "Start / Join",
                    key=f"doctor_start_{appointment['appointment_id']}",
                ):
                    if appointment["status"] == "confirmed":
                        result = _with_api_error(
                            lambda: update_appointment(appointment["appointment_id"], {"status": "in_progress"})
                        )
                        if result is None:
                            return
                    st.session_state.doctor_active_appointment_id = appointment["appointment_id"]
                    st.session_state.doctor_active_room = appointment["consultation_room_id"]
                    st.session_state.consultation_room_input_doctor = appointment["consultation_room_id"]
                    _set_flash(f"Consultation room {appointment['consultation_room_id']} is ready.", "info")
                    st.rerun()
            with button_cols[1]:
                if appointment["status"] == "in_progress" and st.button(
                    "Mark Completed",
                    key=f"doctor_complete_{appointment['appointment_id']}",
                ):
                    result = _with_api_error(
                        lambda: update_appointment(appointment["appointment_id"], {"status": "completed"})
                    )
                    if result is not None:
                        _set_flash(f"Appointment {appointment['appointment_id']} marked completed.", "success")
                        st.rerun()
            with button_cols[2]:
                if appointment["status"] == "confirmed" and st.button(
                    "Cancel",
                    key=f"doctor_cancel_{appointment['appointment_id']}",
                ):
                    result = _with_api_error(
                        lambda: update_appointment(appointment["appointment_id"], {"status": "cancelled"})
                    )
                    if result is not None:
                        _set_flash(f"Appointment {appointment['appointment_id']} cancelled.", "warning")
                        st.rerun()
            with button_cols[3]:
                st.caption(f"Updated: {_format_datetime(appointment['updated_at'])}")

            if appointment["status"] == "confirmed":
                st.markdown("#### Reschedule")
                schedule_cols = st.columns(3)
                with schedule_cols[0]:
                    current_time = _parse_iso(appointment["scheduled_time"]) or datetime.now().astimezone()
                    new_date = st.date_input(
                        "New date",
                        value=current_time.date(),
                        key=f"doctor_reschedule_date_{appointment['appointment_id']}",
                    )
                with schedule_cols[1]:
                    new_time = st.time_input(
                        "New time",
                        value=current_time.time().replace(second=0, microsecond=0),
                        key=f"doctor_reschedule_time_{appointment['appointment_id']}",
                    )
                with schedule_cols[2]:
                    if st.button("Apply", key=f"doctor_reschedule_apply_{appointment['appointment_id']}"):
                        payload = {"scheduled_time": _combine_to_iso(new_date, new_time)}
                        result = _with_api_error(lambda: update_appointment(appointment["appointment_id"], payload))
                        if result is not None:
                            _set_flash(f"Appointment {appointment['appointment_id']} rescheduled.", "success")
                            st.rerun()


def _render_doctor_consultation(appointments: list[dict[str, Any]]) -> None:
    st.markdown("### Consultation Center")
    active_options = [item for item in appointments if item["status"] in {"confirmed", "in_progress"}]
    if not active_options:
        st.info("No confirmed or live appointments are available for consultation.")
        return

    option_map = {item["appointment_id"]: item for item in active_options}
    default_id = st.session_state.get("doctor_active_appointment_id", active_options[0]["appointment_id"])
    selected_id = st.selectbox(
        "Appointment",
        options=list(option_map.keys()),
        index=list(option_map.keys()).index(default_id) if default_id in option_map else 0,
        format_func=lambda item: (
            f"{item} • {option_map[item]['patient_name']} • {_status_label(option_map[item]['status'])}"
        ),
    )
    selected = option_map[selected_id]

    if selected["status"] == "confirmed" and st.button("Start Consultation", key=f"doctor_consult_start_{selected_id}"):
        result = _with_api_error(lambda: update_appointment(selected_id, {"status": "in_progress"}))
        if result is not None:
            st.session_state.doctor_active_appointment_id = selected_id
            st.session_state.doctor_active_room = selected["consultation_room_id"]
            st.session_state.consultation_room_input_doctor = selected["consultation_room_id"]
            st.rerun()

    st.caption(
        f"Patient: {selected['patient_name']} • Room: `{selected['consultation_room_id']}` • "
        f"Scheduled: {_format_datetime(selected['scheduled_time'])}"
    )
    st.session_state.consultation_room_input_doctor = selected["consultation_room_id"]
    consultation_module.render(
        role="Doctor",
        default_room_id=selected["consultation_room_id"],
        section_title=f"Consultation with {selected['patient_name']}",
    )


def _render_doctor_feedback(doctor: dict[str, Any]) -> None:
    st.markdown("### Patient Feedback")
    summary = _with_api_error(lambda: feedback_summary(doctor_id=doctor["id"]))
    feedback_entries = _with_api_error(lambda: list_feedback(doctor_id=doctor["id"]))
    if summary is None or feedback_entries is None:
        return

    metric_cols = st.columns(5)
    metric_cols[0].metric("Total Feedback", summary["total_feedback"])
    metric_cols[1].metric("Avg Rating", f"{summary['avg_rating']}/5")
    metric_cols[2].metric("Communication", f"{summary['avg_communication']}/5")
    metric_cols[3].metric("Wait Time", f"{summary['avg_wait_time']}/5")
    metric_cols[4].metric("Recommend Rate", f"{summary['recommend_percent']}%")

    if not feedback_entries:
        st.info("No feedback available yet.")
        return

    chart_cols = st.columns(2)
    with chart_cols[0]:
        rating_df = pd.DataFrame(feedback_entries)
        rating_counts = rating_df["rating"].value_counts().sort_index().reset_index()
        rating_counts.columns = ["Rating", "Count"]
        fig_rating = px.bar(
            rating_counts,
            x="Rating",
            y="Count",
            color="Rating",
            color_discrete_sequence=["#ef4444", "#f97316", "#f59e0b", "#10b981", "#2563eb"],
            title="Rating Distribution",
        )
        st.plotly_chart(fig_rating, use_container_width=True)

    with chart_cols[1]:
        trend_df = pd.DataFrame(feedback_entries)
        trend_df["created_at"] = pd.to_datetime(trend_df["created_at"])
        trend_df["Date"] = trend_df["created_at"].dt.date
        grouped = trend_df.groupby("Date").agg({"rating": "mean"}).reset_index()
        grouped["Date"] = pd.to_datetime(grouped["Date"])
        fig_trend = px.line(
            grouped,
            x="Date",
            y="rating",
            markers=True,
            title="Average Rating Over Time",
            color_discrete_sequence=["#2563eb"],
        )
        fig_trend.update_layout(yaxis_range=[0, 5])
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("#### Recent Comments")
    for item in feedback_entries[:8]:
        with st.expander(
            f"{item['patient_name']} • {item['rating']}/5 • {_format_datetime(item['created_at'])}",
            expanded=False,
        ):
            st.markdown(f"**Communication:** {item['communication']}/5")
            st.markdown(f"**Wait Time:** {item['wait_time']}/5")
            st.markdown(f"**Recommend:** {'Yes' if item['recommend'] else 'No'}")
            st.markdown(f"**Comment:** {item.get('comment') or 'No comment'}")


def render_doctor_dashboard(auth_user: Optional[dict[str, Any]] = None) -> None:
    ui.inject_global_css()
    st.markdown("## Doctor Teleconsultation Workspace")
    _render_flash()

    if not _ensure_backend():
        return

    doctors = _with_api_error(list_doctors)
    if doctors is None:
        return

    doctor_map = {doctor["id"]: doctor for doctor in doctors}
    if auth_user is not None:
        selected_doctor_id = auth_user["linked_profile_id"]
        doctor = doctor_map.get(selected_doctor_id)
        if doctor is None:
            st.error("The signed-in doctor profile could not be found.")
            return
        st.caption(f"Signed in as {auth_user['full_name']} • {auth_user['email']}")
    else:
        default_doctor_id = st.session_state.get("selected_doctor_id", doctors[0]["id"])
        selected_doctor_id = st.sidebar.selectbox(
            "Doctor Profile",
            options=list(doctor_map.keys()),
            index=list(doctor_map.keys()).index(default_doctor_id) if default_doctor_id in doctor_map else 0,
            format_func=lambda item: f"{doctor_map[item]['name']} • {_status_label(doctor_map[item]['status'])}",
        )
        st.session_state.selected_doctor_id = selected_doctor_id
        doctor = doctor_map[selected_doctor_id]
    appointments = _with_api_error(lambda: list_appointments(user_id=doctor["id"], role="doctor"))
    if appointments is None:
        return

    nav = st.sidebar.radio(
        "Workspace",
        ["Dashboard", "Appointments", "Consultation", "Notifications", "Feedback"],
        key="doctor_workspace_nav",
    )

    with st.sidebar:
        st.markdown("---")
        _render_doctor_status_controls(doctor)
        st.markdown("---")
        _render_doctor_cards(doctors, "Doctor Listing & Availability")

    if nav == "Dashboard":
        _render_doctor_dashboard_overview(doctor, doctors, appointments)
    elif nav == "Appointments":
        _render_doctor_appointments(doctor, appointments)
    elif nav == "Consultation":
        _render_doctor_consultation(appointments)
    elif nav == "Notifications":
        _render_notification_list(doctor["id"], "Notifications & Reminders", f"doctor_notifications_{doctor['id']}")
    elif nav == "Feedback":
        _render_doctor_feedback(doctor)

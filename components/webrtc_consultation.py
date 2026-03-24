"""
Consultation launcher for the standalone WebRTC room page.
"""
from __future__ import annotations

import os
from typing import Optional
from urllib.parse import quote, urlencode

import streamlit as st

from backend.consultation_auth import issue_consultation_token

from .platform_api import API_BASE_URL


class ConsultationModule:
    """Launches a signed consultation room from the dashboard."""

    @staticmethod
    def _get_display_name(role: str, participant_name: Optional[str]) -> tuple[str, str]:
        role_key = role.lower()
        session_key = f"consultation_display_name_{role_key}"
        default_name = (participant_name or role.title()).strip()
        if session_key not in st.session_state:
            st.session_state[session_key] = default_name
        return session_key, st.session_state[session_key]

    @staticmethod
    def _consultation_url(room_id: str, participant_id: str, role: str, display_name: str) -> str:
        token = issue_consultation_token(room_id, participant_id, role)
        params = urlencode(
            {
                "participant_id": participant_id,
                "role": role.lower(),
                "display_name": display_name,
                "token": token,
            }
        )
        room_path = quote(room_id, safe="")
        return f"{API_BASE_URL}/consultations/{room_path}?{params}"

    @staticmethod
    def _render_launch_link(url: str) -> None:
        if hasattr(st, "link_button"):
            st.link_button("Open Video Consultation", url, type="primary", use_container_width=True)
            return

        st.markdown(
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">'
            '<button style="width:100%;padding:0.75rem 1rem;border:0;border-radius:0.75rem;'
            'background:#0f766e;color:white;font-weight:600;cursor:pointer;">'
            "Open Video Consultation"
            "</button></a>",
            unsafe_allow_html=True,
        )

    def render(
        self,
        role: str,
        default_room_id: str = "ER-001",
        section_title: str = "Live Consultation",
        *,
        participant_id: Optional[str] = None,
        participant_name: Optional[str] = None,
        appointment_id: Optional[str] = None,
    ) -> None:
        st.markdown(f"### {section_title}")

        display_name_key, current_display_name = self._get_display_name(role, participant_name)
        room_input_key = f"consultation_room_input_{role.lower()}"

        col1, col2 = st.columns([2, 2])
        with col1:
            room_id = st.text_input(
                "Consultation Room ID",
                value=default_room_id,
                key=room_input_key,
                help="This room is created from the appointment record and shared with the matched participant.",
            ).strip()
        with col2:
            display_name = st.text_input(
                "Display Name",
                value=current_display_name,
                key=display_name_key,
                help="Shown in the room participant list and chat feed.",
            ).strip()

        if not room_id:
            st.warning("Enter a consultation room ID to continue.")
            return

        if not participant_id:
            st.warning("Consultation launch is only available from the appointment-backed patient and doctor dashboards.")
            return

        launch_url = self._consultation_url(
            room_id=room_id,
            participant_id=participant_id,
            role=role,
            display_name=display_name or participant_name or role.title(),
        )

        st.info(
            "The call opens in a dedicated browser page so camera and microphone permissions work reliably. "
            "Keep the dashboard open if you still want appointment controls."
        )

        meta_col1, meta_col2, meta_col3 = st.columns(3)
        meta_col1.metric("Room", room_id)
        meta_col2.metric("Role", role.title())
        meta_col3.metric("Appointment", appointment_id or "Direct launch")

        self._render_launch_link(launch_url)
        st.caption("Open the room from both the patient and doctor sides to establish the peer connection.")

        if not os.getenv("BIOSYNC_TURN_URL", "").strip():
            st.caption("TURN is not configured. Calls may fail on restrictive networks until `BIOSYNC_TURN_URL` is set.")


consultation_module = ConsultationModule()

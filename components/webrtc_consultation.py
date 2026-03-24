"""
WebRTC consultation module for real-time video and text chat.
"""

from datetime import datetime
from threading import Lock
from typing import Dict, List
from uuid import uuid4

import streamlit as st
from streamlit_webrtc import RTCConfiguration, WebRtcMode, webrtc_streamer


@st.cache_resource
def _get_consultation_store() -> Dict[str, object]:
    """Create a shared in-memory store for room state across Streamlit sessions."""
    return {"rooms": {}, "lock": Lock()}


class ConsultationModule:
    """Room-based consultation UI with WebRTC stream and text chat."""

    def __init__(self) -> None:
        self._rtc_configuration = RTCConfiguration(
            {
                "iceServers": [
                    {"urls": ["stun:stun.l.google.com:19302"]},
                    {"urls": ["stun:stun1.l.google.com:19302"]},
                ]
            }
        )

    @staticmethod
    def _get_session_identity(role: str) -> Dict[str, str]:
        role_key = role.lower()
        session_id_key = f"consultation_session_id_{role_key}"
        display_name_key = f"consultation_display_name_{role_key}"

        if session_id_key not in st.session_state:
            st.session_state[session_id_key] = str(uuid4())[:8]

        default_name = f"{role.title()}-{st.session_state[session_id_key][:4]}"
        if display_name_key not in st.session_state:
            st.session_state[display_name_key] = default_name

        return {
            "session_id": st.session_state[session_id_key],
            "display_name": st.session_state[display_name_key],
            "display_name_key": display_name_key,
        }

    @staticmethod
    def _ensure_room(room_id: str) -> None:
        store = _get_consultation_store()
        with store["lock"]:
            rooms = store["rooms"]
            if room_id not in rooms:
                rooms[room_id] = {
                    "participants": {},
                    "messages": [],
                }

    @staticmethod
    def _register_participant(room_id: str, session_id: str, role: str, display_name: str) -> None:
        store = _get_consultation_store()
        with store["lock"]:
            room = store["rooms"][room_id]
            room["participants"][session_id] = {
                "role": role,
                "display_name": display_name,
                "last_seen": datetime.utcnow().isoformat(),
            }

    @staticmethod
    def _get_room_snapshot(room_id: str) -> Dict[str, List[Dict[str, str]]]:
        store = _get_consultation_store()
        with store["lock"]:
            room = store["rooms"][room_id]
            return {
                "participants": list(room["participants"].values()),
                "messages": list(room["messages"]),
            }

    @staticmethod
    def _append_message(room_id: str, role: str, display_name: str, message: str) -> None:
        if not message:
            return

        store = _get_consultation_store()
        with store["lock"]:
            room = store["rooms"][room_id]
            room["messages"].append(
                {
                    "role": role,
                    "display_name": display_name,
                    "message": message.strip(),
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                }
            )

            # Keep a bounded in-memory history per room.
            room["messages"] = room["messages"][-100:]

    def render(self, role: str, default_room_id: str = "ER-001", section_title: str = "Live Consultation") -> None:
        """Render a full consultation surface for the selected role."""
        st.markdown(f"### 💬 {section_title}")

        identity = self._get_session_identity(role)
        room_input_key = f"consultation_room_input_{role.lower()}"

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            room_id = st.text_input(
                "Consultation Room ID",
                value=default_room_id,
                key=room_input_key,
                help="Share this room ID with the other participant.",
            ).strip()

        with col2:
            display_name = st.text_input(
                "Display Name",
                value=identity["display_name"],
                key=identity["display_name_key"],
                help="This name appears in room participants and chat.",
            ).strip()

        with col3:
            st.caption("Session")
            st.code(identity["session_id"])

        if not room_id:
            st.warning("Please enter a room ID to start consultation.")
            return

        self._ensure_room(room_id)
        self._register_participant(room_id, identity["session_id"], role, display_name or identity["display_name"])

        snapshot = self._get_room_snapshot(room_id)
        participants = snapshot["participants"]
        messages = snapshot["messages"]

        st.info(
            f"Room {room_id} active: {len(participants)} participant(s) connected. "
            "Start camera/mic below for WebRTC consultation."
        )

        participant_line = " | ".join(
            [f"{p['display_name']} ({p['role']})" for p in participants]
        )
        if participant_line:
            st.caption(f"Participants: {participant_line}")

        webrtc_streamer(
            key=f"webrtc_consultation_{role.lower()}_{room_id}_{identity['session_id']}",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=self._rtc_configuration,
            media_stream_constraints={"video": True, "audio": True},
            async_processing=True,
        )

        st.markdown("#### Room Chat")
        for entry in messages:
            chat_role = "assistant" if entry["role"].lower() == "doctor" else "user"
            with st.chat_message(chat_role):
                st.markdown(
                    f"**{entry['display_name']}** · {entry['timestamp']}  \n{entry['message']}"
                )

        prompt = st.chat_input("Type a message for the consultation room")
        if prompt:
            self._append_message(room_id, role, display_name or identity["display_name"], prompt)
            st.rerun()


consultation_module = ConsultationModule()

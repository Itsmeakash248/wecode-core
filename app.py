"""
BioSync Tele-Rescue - Healthcare Telemedicine Dashboard
"""
from __future__ import annotations

import streamlit as st

from components.auth_portal import render_auth_portal
from components.pages import DoctorDashboard, LandingPage, PatientDashboard


HOME_VIEW = "🏠 Home"
AUTH_VIEW = "🔐 Access Portal"
PATIENT_VIEW = "👤 Patient Dashboard"
DOCTOR_VIEW = "👨‍⚕️ Doctor Platform"
ROLE_TO_VIEW = {"patient": PATIENT_VIEW, "doctor": DOCTOR_VIEW}
VIEW_TO_ROLE = {PATIENT_VIEW: "patient", DOCTOR_VIEW: "doctor"}


st.set_page_config(
    page_title="BioSync Tele-Rescue - Healthcare Dashboard",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/biosync-tele-rescue",
        "Report a bug": "https://github.com/your-repo/biosync-tele-rescue/issues",
        "About": """
        ## BioSync Tele-Rescue

        **Autonomous Edge-AI Teleconsultation Platform**

        Revolutionizing emergency healthcare by automatically connecting patients to doctors during critical moments.
        """,
    },
)


def _initialize_session_state() -> None:
    defaults = {
        "view": HOME_VIEW,
        "monitoring": False,
        "emergency_feed": False,
        "auth_user": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _logout() -> None:
    keys_to_clear = [
        key
        for key in st.session_state.keys()
        if key.startswith("consultation_")
        or key.startswith("patient_")
        or key.startswith("doctor_")
        or key in {"auth_user", "selected_patient_id", "selected_doctor_id", "platform_flash", "requested_role", "main_navigation"}
    ]
    for key in keys_to_clear:
        del st.session_state[key]
    st.session_state.view = HOME_VIEW


def _render_sidebar(auth_user):
    st.sidebar.title("🚑 BioSync Tele-Rescue")
    st.sidebar.markdown("---")

    if auth_user:
        role_view = ROLE_TO_VIEW[auth_user["role"]]
        if st.session_state.view not in {HOME_VIEW, role_view}:
            st.session_state.view = role_view

        view = st.sidebar.selectbox(
            "Navigation",
            [HOME_VIEW, role_view],
            index=[HOME_VIEW, role_view].index(st.session_state.view),
            key="main_navigation",
        )
        st.sidebar.caption(f"{auth_user['full_name']} • {auth_user['role'].title()}")
        st.sidebar.caption(auth_user["email"])
        if st.sidebar.button("Log Out", key="logout_button"):
            _logout()
            st.rerun()
    else:
        requested_role = None
        current_view = st.session_state.view
        if current_view in VIEW_TO_ROLE:
            requested_role = VIEW_TO_ROLE[current_view]
            current_view = AUTH_VIEW
        elif current_view not in {HOME_VIEW, AUTH_VIEW}:
            current_view = HOME_VIEW

        view = st.sidebar.selectbox(
            "Navigation",
            [HOME_VIEW, AUTH_VIEW],
            index=[HOME_VIEW, AUTH_VIEW].index(current_view),
            key="main_navigation",
        )
        st.session_state.requested_role = requested_role

    if view != st.session_state.view:
        st.session_state.view = view
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("**BioSync Tele-Rescue**")
    st.sidebar.markdown("*Secure Emergency Teleconsultation Platform*")
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2026 WeCode Team")


def main() -> None:
    _initialize_session_state()
    auth_user = st.session_state.get("auth_user")
    _render_sidebar(auth_user)

    current_view = st.session_state.view
    preferred_role = st.session_state.get("requested_role")

    if current_view == HOME_VIEW:
        LandingPage.render()
        if not auth_user:
            st.info("Sign in to book appointments, join consultations, and manage feedback.")
        return

    if current_view == AUTH_VIEW:
        auth_result = render_auth_portal(preferred_role=preferred_role)
        if auth_result is not None:
            st.session_state.auth_user = auth_result["user"]
            st.session_state.view = ROLE_TO_VIEW[auth_result["user"]["role"]]
            st.session_state.requested_role = None
            st.session_state.pop("main_navigation", None)
            st.rerun()
        return

    if not auth_user:
        st.warning("Please sign in to access the platform workspace.")
        auth_result = render_auth_portal(preferred_role=preferred_role or VIEW_TO_ROLE.get(current_view))
        if auth_result is not None:
            st.session_state.auth_user = auth_result["user"]
            st.session_state.view = ROLE_TO_VIEW[auth_result["user"]["role"]]
            st.session_state.requested_role = None
            st.session_state.pop("main_navigation", None)
            st.rerun()
        return

    expected_view = ROLE_TO_VIEW[auth_user["role"]]
    if current_view != expected_view:
        st.session_state.view = expected_view
        st.rerun()

    if auth_user["role"] == "patient":
        PatientDashboard.render(auth_user=auth_user)
    else:
        DoctorDashboard.render(auth_user=auth_user)


if __name__ == "__main__":
    main()

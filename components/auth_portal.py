"""
Streamlit authentication portal for login and account creation.
"""
from __future__ import annotations

from typing import Any, Optional

import streamlit as st

from .platform_api import ApiError, BackendUnavailable, login, register
from .ui_components import ui


DEMO_ACCOUNTS = [
    {"role": "Patient", "email": "john.doe@biosync.local", "password": "patient123"},
    {"role": "Doctor", "email": "priya.sharma@biosync.local", "password": "doctor123"},
]


def _call_auth(action):
    try:
        return action()
    except BackendUnavailable as exc:
        st.error(str(exc))
        st.caption("Use `bash start.sh` from the repo root before opening the portal.")
        return None
    except ApiError as exc:
        st.error(str(exc))
        return None


def render_auth_portal(preferred_role: Optional[str] = None) -> Optional[dict[str, Any]]:
    ui.inject_global_css()
    st.markdown("## Access Portal")
    st.caption("Log in with an existing account or create a new patient/doctor account.")

    login_tab, register_tab = st.tabs(["Log In", "Create Account"])
    auth_result: Optional[dict[str, Any]] = None

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="name@example.com", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log In")

            if submitted:
                auth_result = _call_auth(lambda: login({"email": email, "password": password}))
                if auth_result is not None:
                    st.success(auth_result["message"])

    with register_tab:
        role_options = ["patient", "doctor"]
        initial_role = preferred_role if preferred_role in role_options else "patient"
        with st.form("register_form"):
            account_role = st.radio(
                "Account Type",
                role_options,
                index=role_options.index(initial_role),
                horizontal=True,
                format_func=lambda value: value.title(),
                key="register_role",
            )
            full_name = st.text_input("Full Name", key="register_full_name")
            email = st.text_input("Email Address", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")

            if account_role == "patient":
                age = st.number_input("Age", min_value=0, max_value=120, value=30, step=1, key="register_age")
                condition = st.text_input("Primary Condition", key="register_condition")
                risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High"], key="register_risk_level")
                payload = {
                    "full_name": full_name,
                    "email": email,
                    "password": password,
                    "role": account_role,
                    "age": int(age),
                    "condition": condition,
                    "risk_level": risk_level,
                }
            else:
                specialty = st.text_input("Specialty", key="register_specialty")
                experience = st.number_input(
                    "Years of Experience",
                    min_value=0,
                    max_value=60,
                    value=5,
                    step=1,
                    key="register_experience",
                )
                payload = {
                    "full_name": full_name,
                    "email": email,
                    "password": password,
                    "role": account_role,
                    "specialty": specialty,
                    "experience": int(experience),
                }

            submitted = st.form_submit_button("Create Account")

            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    auth_result = _call_auth(lambda: register(payload))
                    if auth_result is not None:
                        st.success(auth_result["message"])

    with st.expander("Demo Credentials", expanded=False):
        st.caption("Seeded accounts on first run:")
        for account in DEMO_ACCOUNTS:
            st.markdown(
                f"**{account['role']}**: `{account['email']}` / `{account['password']}`"
            )

    st.markdown("---")
    st.markdown("#### 🚀 Quick Access")
    st.caption("Skip sign-in and explore the platform as a guest. Some features may be limited.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 Enter as Patient", use_container_width=True, key="guest_patient_btn"):
            auth_result = {
                "message": "Entered as Guest Patient.",
                "user": {
                    "id": "guest-patient",
                    "role": "patient",
                    "full_name": "Guest Patient",
                    "email": "guest.patient@demo.local",
                    "linked_profile_id": None,
                },
            }
    with col2:
        if st.button("👨‍⚕️ Enter as Doctor", use_container_width=True, key="guest_doctor_btn"):
            auth_result = {
                "message": "Entered as Guest Doctor.",
                "user": {
                    "id": "guest-doctor",
                    "role": "doctor",
                    "full_name": "Guest Doctor",
                    "email": "guest.doctor@demo.local",
                    "linked_profile_id": None,
                },
            }

    return auth_result

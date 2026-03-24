"""
BioSync Tele-Rescue - Healthcare Telemedicine Dashboard
A modern, AI-powered teleconsultation platform for emergency healthcare

Author: WeCode Team
HackArena 2K26 Healthcare Track
"""

import streamlit as st
from components.pages import LandingPage, PatientDashboard, DoctorDashboard
from components.ui_components import ui

# Configure the Streamlit app
st.set_page_config(
    page_title="BioSync Tele-Rescue - Healthcare Dashboard",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/biosync-tele-rescue',
        'Report a bug': 'https://github.com/your-repo/biosync-tele-rescue/issues',
        'About': '''
        ## BioSync Tele-Rescue

        **Autonomous Edge-AI Teleconsultation Platform**

        Revolutionizing emergency healthcare by automatically connecting patients to doctors during critical moments.

        ---
        Developed for HackArena 2K26 Healthcare Track
        Team: WeCode Together
        '''
    }
)

def main():
    """Main application entry point"""

    # Initialize session state
    if 'view' not in st.session_state:
        st.session_state.view = "🏠 Home"

    if 'monitoring' not in st.session_state:
        st.session_state.monitoring = False

    if 'emergency_feed' not in st.session_state:
        st.session_state.emergency_feed = False

    # Sidebar navigation
    st.sidebar.title("🚑 BioSync Tele-Rescue")
    st.sidebar.markdown("---")

    view = st.sidebar.selectbox(
        "Navigation",
        ["🏠 Home", "👤 Patient Dashboard", "👨‍⚕️ Doctor Platform"],
        index=["🏠 Home", "👤 Patient Dashboard", "👨‍⚕️ Doctor Platform"].index(st.session_state.view),
        key="main_navigation"
    )

    # Update session state when navigation changes
    if view != st.session_state.view:
        st.session_state.view = view
        st.rerun()

    # Render the selected page
    if view == "🏠 Home":
        LandingPage.render()
    elif view == "👤 Patient Dashboard":
        PatientDashboard.render()
    elif view == "👨‍⚕️ Doctor Platform":
        DoctorDashboard.render()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**BioSync Tele-Rescue**")
    st.sidebar.markdown("*Emergency Teleconsultation Platform*")
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2024 WeCode Team - HackArena 2K26")

if __name__ == "__main__":
    main()
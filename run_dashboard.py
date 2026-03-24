#!/usr/bin/env python3
"""
BioSync Tele-Rescue Dashboard Launcher
Healthcare Telemedicine Platform
"""

import os
import sys
import subprocess
import platform

def print_header():
    print("=" * 40)
    print("  BioSync Tele-Rescue Dashboard")
    print("  Healthcare Telemedicine Platform")
    print("=" * 40)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7+ is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def install_dependencies():
    """Install required dependencies"""
    print("Installing/updating dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to install dependencies")
        return False

def run_streamlit():
    """Run the Streamlit application"""
    print()
    print("Starting BioSync Tele-Rescue Dashboard...")
    print()
    print("The application will open in your default browser")
    print("Press Ctrl+C to stop the server")
    print()

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "true",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print()
        print("Application stopped by user.")
    except Exception as e:
        print(f"ERROR: Failed to start application: {e}")

def main():
    print_header()

    # Check if app.py exists
    if not os.path.exists("app.py"):
        print("ERROR: app.py not found. Please run this script from the project root directory.")
        input("Press Enter to exit...")
        return 1

    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return 1

    # Install dependencies
    if not install_dependencies():
        input("Press Enter to exit...")
        return 1

    # Run the application
    run_streamlit()

    print()
    print("Application stopped.")
    input("Press Enter to exit...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
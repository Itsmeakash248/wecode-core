#!/bin/bash

echo "========================================"
echo "  BioSync Tele-Rescue Dashboard"
echo "  Healthcare Telemedicine Platform"
echo "========================================"
echo

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found. Please run this script from the project root directory."
    exit 1
fi

echo "Checking Python installation..."
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo
echo "Installing/updating dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "Starting BioSync Tele-Rescue Dashboard..."
echo
echo "The application will open in your default browser"
echo "Press Ctrl+C to stop the server"
echo

$PYTHON_CMD -m streamlit run app.py --server.headless true --server.port 8501

echo
echo "Application stopped."
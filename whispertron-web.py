#!/usr/bin/env python3
import os
import sys
import subprocess

# Ensure we're in the project directory
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

# Check if virtual environment exists
venv_python = os.path.join(project_root, ".venv", "bin", "python3")

def install_web_dependencies():
    """Install web-specific dependencies"""
    print("Installing web dependencies...")
    
    # Install web requirements
    web_requirements = os.path.join(project_root, "web", "requirements.txt")
    if os.path.exists(web_requirements):
        subprocess.run([venv_python, "-m", "pip", "install", "-r", web_requirements], check=True)
    else:
        # Install manually if requirements file doesn't exist
        subprocess.run([venv_python, "-m", "pip", "install", "Flask==2.3.3", "Flask-SocketIO==5.3.6", "python-socketio==5.9.0", "eventlet==0.33.3"], check=True)
    
    print("Web dependencies installed successfully!")

def launch_web_app():
    """Launch the web application"""
    web_app_path = os.path.join(project_root, "web", "app.py")
    
    if not os.path.exists(web_app_path):
        print("Error: Web application not found at web/app.py")
        sys.exit(1)
    
    print("Starting WhisperTron Web Interface...")
    print("Access the web interface at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    # Change to web directory and launch
    web_dir = os.path.join(project_root, "web")
    os.chdir(web_dir)
    
    # Launch the Flask app
    os.execl(venv_python, venv_python, "app.py")

if __name__ == "__main__":
    if not os.path.exists(venv_python):
        print("Error: Virtual environment not found. Please run setup.sh first.")
        sys.exit(1)
    
    # Check if web dependencies are installed
    try:
        subprocess.run([venv_python, "-c", "import flask, flask_socketio"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        install_web_dependencies()
    
    launch_web_app()
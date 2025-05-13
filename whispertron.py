#!/usr/bin/env python3
import os
import sys

# Ensure we're in the project directory
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

# Ensure the virtual environment is active
venv_python = os.path.join(project_root, ".venv", "bin", "python3")

# Launch the UI
if __name__ == "__main__":
    if os.path.exists(venv_python):
        os.execl(venv_python, venv_python, "ui/app.py")
    else:
        print("Error: Virtual environment not found. Please run setup.sh first.")
        sys.exit(1) 
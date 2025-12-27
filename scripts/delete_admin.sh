#!/bin/bash

# Script to delete admin user for KHolder

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KHOLDER_DIR="$PROJECT_DIR/kholder"
VENV_DIR="$PROJECT_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python3"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run the command
cd "$KHOLDER_DIR"
"$VENV_PYTHON" manage.py delete_admin
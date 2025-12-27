#!/bin/bash

# Reset database script for KHolder

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KHOLDER_DIR="$PROJECT_DIR/kholder"
VENV_DIR="$PROJECT_DIR/venv"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Remove database
rm -f "$KHOLDER_DIR/db/db.sqlite3"

# Remove migration file in keys
rm -f "$KHOLDER_DIR/keys/migrations/0001_initial.py"

# Run makemigrations
python "$KHOLDER_DIR/manage.py" makemigrations

# Run migrate
python "$KHOLDER_DIR/manage.py" migrate
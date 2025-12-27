#!/bin/bash

# Setup script for KHolder

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KHOLDER_DIR="$PROJECT_DIR/kholder"
VENV_DIR="$PROJECT_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python3"
VENV_GUNICORN="$VENV_DIR/bin/gunicorn"
SYSTEMD_DIR="/etc/systemd/system"

# ANSI color codes
BLUE='\033[34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_step() {
    echo -e "${BLUE}$1${NC}"
}

# Check if running as root for systemd operations
if [[ $EUID -ne 0 ]]; then
    echo "This script needs to run with sudo for systemd operations."
    exit 1
fi

print_step "Setting up KHolder..."

# Create Python virtual environment if it doesn't exist
if [[ ! -d "$VENV_DIR" ]]; then
    print_step "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
print_step "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
print_step "Installing dependencies..."
pip install -e "$PROJECT_DIR"

# Generate .env if it doesn't exist
if [[ ! -f "$KHOLDER_DIR/.env" ]]; then
    print_step "Generating .env file..."
    "$VENV_PYTHON" "$PROJECT_DIR/scripts/generate_dotenv.py"
fi

# Run database migrations
print_step "Running database migrations..."
cd "$KHOLDER_DIR"
"$VENV_PYTHON" manage.py migrate

# Collect static files
print_step "Collecting static files..."
"$VENV_PYTHON" manage.py collectstatic --noinput

print_step "Creating systemd services..."

# Generate kholder.service
cat > "$SYSTEMD_DIR/kholder.service" << EOF
[Unit]
Description=KHolder Django Server
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$KHOLDER_DIR
ExecStart=$VENV_GUNICORN --bind unix:/tmp/kholder.sock kholder.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Generate kholder-web.service
cat > "$SYSTEMD_DIR/kholder-web.service" << EOF
[Unit]
Description=KHolder Django Web Server
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$KHOLDER_DIR
ExecStart=$VENV_PYTHON manage.py runserver 0.0.0.0:8008
Restart=always
RestartSec=5
EOF

# Reload systemd daemon
systemctl daemon-reload

print_step "Setup complete!"
echo "Services installed. Use:"
echo "sudo systemctl enable kholder.service  # to enable main service (unix socket, auto-start)"
echo "sudo systemctl start kholder-web.service  # to start web service (TCP port, optional)"
echo "sudo systemctl start kholder.service  # to start main service"


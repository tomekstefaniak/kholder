# KHolder

**KHolder** (Keyholder) is a secure, local key storage application built with Django. It stores encrypted secrets (keys) protected by per-key passwords and exposes a REST API intended for local access.

Important: the production deployment runs on Linux under `systemd` and serves the API via a Unix domain socket (UDS) (by default `/tmp/kholder.sock`). There is also an optional `kholder-web` service which exposes a browser-accessible web UI; its root path `/` shows a small menu with links to the Swagger API documentation and the Django admin panel.

Keys are plain text strings (passwords, API keys, tokens). They are encrypted and stored as binary data; the default maximum is ~8192 bytes (configurable in the Django model).

## Table of Contents

1. [Features](#1-features)
2. [Requirements](#2-requirements)
3. [Installation](#3-installation)
4. [Running the Application](#4-running-the-application)
   - [Manual (Development)](#manual-development)
   - [Via Systemd Services (Production)](#via-systemd-services-production)
5. [Key Management](#6-key-management)
6. [API Documentation](#5-api-documentation)
7. [Django Admin](#7-django-admin)
8. [Security Notes](#8-security-notes)
9. [Services](#9-services)
10. [License](#10-license)

## 1. Features

1. **Password-Protected Encryption**: Keys are encrypted using Fernet (AES) with PBKDF2-derived keys from user-provided passwords.
2. **REST API**: Full CRUD operations for keys via JSON endpoints. No authentication required beyond per-key passwords.
3. **Unix Domain Socket**: Secure local communication, no network exposure.
4. **Django Admin Panel**: Web interface for managing the application.
5. **Systemd Integration**: Easy deployment as system services.
6. **Database**: Uses Django's default SQLite3 database for local storage.
7. **Index Page**: Root path `/` displays an HTML page with navigation links to admin and docs. Multiple services can access it concurrently (SQLite supports this), but for high load consider PostgreSQL.

## 2. Requirements

- Python 3.10+
- Linux (recommended for production; required for `systemd`-based deployment and Unix domain sockets)

## 3. Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd kholder
   ```

2. Run the setup script (requires sudo for systemd):
   ```bash
   sudo ./setup.sh
   ```
   This will:
   - Create a Python virtual environment.
   - Install dependencies.
   - Generate a `.env` file with a random `SECRET_KEY`.
   - Run database migrations.
   - Collect static files.
   - Set up systemd services.

3. The application is ready to run.

## 4. Running the Application

### Manual (Development)

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Start the Django development server:
   ```bash
   cd kholder
   python manage.py runserver
   ```
   Server runs on `http://127.0.0.1:8008`.

3. Initialize admin user (optional, for Django admin panel access):
   ```bash
   python manage.py init_admin
   ```

### Via Systemd Services (Production)

KHolder is packaged to run as `systemd` services on Linux. The primary `kholder.service` runs Gunicorn and listens on a Unix domain socket (default `/tmp/kholder.sock`) for secure, local-only access. This is the recommended production mode.

Basic steps:

1. Initialize or create the Django admin user (run once):
   ```bash
   ./scripts/init_admin.sh
   ```

2. Enable and start the main socket-backed service (auto-start on boot):
   ```bash
   sudo systemctl enable --now kholder.service
   ```

3. Optionally run the `kholder-web` service to provide direct browser access (binds to TCP port, useful for local debugging or short-lived access):
   ```bash
   sudo systemctl start kholder-web.service
   ```

4. Check service status:
   ```bash
   sudo systemctl status kholder.service
   ```

Notes:

- The Unix socket (`/tmp/kholder.sock`) restricts access to local processes and is safe for local-only deployments; use a reverse proxy (e.g., Nginx) to publish it to HTTP if you need remote access behind proper TLS and access controls.
- The `kholder-web` service is optional; when active it provides a simple web UI where `/` shows a menu linking to the Swagger API docs and the Django admin panel.

### Managing Admin User

The admin user is required only for accessing the Django admin panel (web interface for managing the application). It is not used for API authentication – keys are protected by individual passwords. Creating the admin is a formality to enable panel access.

- Create: `./scripts/init_admin.sh`
- Delete: `./scripts/delete_admin.sh`

## 5. Key Management

Keys are managed via the REST API. Each key has a unique `label` and is encrypted using a password you provide at creation time.

Examples (using `curl` against the production socket):

1. **List keys**
   ```bash
   curl --unix-socket /tmp/kholder.sock http://localhost/keys/
   ```

2. **Create key**
   ```bash
   curl --unix-socket /tmp/kholder.sock -X POST http://localhost/keys/ \
     -H "Content-Type: application/json" \
     -d '{"label": "my-key", "decrypted_key": "secret-value", "password": "strongpass"}'
   ```

3. **Decrypt key**
   ```bash
   curl --unix-socket /tmp/kholder.sock -X POST http://localhost/keys/decrypt/my-key \
     -H "Content-Type: application/json" \
     -d '{"password": "strongpass"}'
   ```

4. **Update key**
   ```bash
   curl --unix-socket /tmp/kholder.sock -X PATCH http://localhost/keys/my-key \
     -H "Content-Type: application/json" \
     -d '{"decrypted_key": "new-secret", "password": "strongpass"}'
   ```

5. **Delete key**
   ```bash
   curl --unix-socket /tmp/kholder.sock -X DELETE http://localhost/keys/my-key
   ```

For local development (Django runserver), point at `http://127.0.0.1:8008` and omit the `--unix-socket` option.

## 6. API Documentation

Interactive Swagger documentation is available when the web service is running. For manual development (Django dev server) visit `http://127.0.0.1:8008/docs/swagger/`. For production (socket-backed) you can expose Swagger via a reverse proxy or by starting `kholder-web`.

The root path `/` (on the `kholder-web` service or any reverse-proxied root) provides a small HTML menu linking to:

- Swagger API documentation
- Django admin panel

This makes it easy to browse the API and jump to the admin UI from a single landing page.

## 7. Django Admin

Access at `http://127.0.0.1:8008/admin/` (manual) or via reverse proxy to Unix socket `/tmp/kholder.sock`. Use the admin user created above. This panel is for managing the Django application itself (e.g., viewing models), not for key operations – keys are handled via the API.

The root path `/` provides links to both the admin panel and API docs.

## 8. Security Notes

- Keys are encrypted locally; passwords are not stored on the server.
- Configure Django production settings (e.g., `ALLOWED_HOSTS`, secure cookies, `DEBUG=False`).
- SQLite is fine for low-concurrency local deployments; switch to PostgreSQL for higher concurrency or multi-host setups.
- The API does not provide global authentication by default — it relies on UDS access restrictions and per-key passwords for protection.
- Thanks to Keyholder, secrets in plain form are stored only in RAM, not in .env files, and thanks to Unix domain sockets, they bypass the network stack, and therefore secrets will not be read by Copilot.

## 9. Services

- `kholder.service` — Primary production service. Runs Gunicorn and listens on a Unix domain socket (default `/tmp/kholder.sock`). Enable for automatic startup.
- `kholder-web.service` — Optional web-facing service (binds to TCP, typically port 8008). When active, its `/` path displays a small menu linking to Swagger docs and the Django admin panel for quick browser access.

### Admin User Management Scripts

Instead of systemd services, use the following shell scripts for managing the Django admin user:

- `scripts/init_admin.sh` — Create the Django admin user.
- `scripts/delete_admin.sh` — Remove the Django admin user.

Run them with `./scripts/init_admin.sh` or `./scripts/delete_admin.sh` from the project root.

## 10. License

MIT License. See LICENSE file.

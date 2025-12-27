from pathlib import Path
from django.core.management.utils import get_random_secret_key


cwd = Path.cwd()
env_path = cwd / "kholder" / ".env"

if not env_path.exists():
    env_path.parent.mkdir(parents=True, exist_ok=True)
    key = get_random_secret_key()
    env_path.write_text(f"SECRET_KEY={key}\n")
    print("Generated new SECRET_KEY")
else:
    print(".env file already exists")

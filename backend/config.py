import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Try loading .env file
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# Database Configuration
# Default to SQLite for zero-config local runs, or use PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'study_companion.db'}")

# Normalize postgresql:// scheme for SQLAlchemy if needed
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Security & API
JWT_SECRET = os.getenv("JWT_SECRET", "aura_deep_focus_secret_key_9981")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    "262576481074-0qemddi96lt1d3buupbreoump4oj4f2e.apps.googleusercontent.com",
)



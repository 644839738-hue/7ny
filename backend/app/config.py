"""
Application configuration.

All settings are read from environment variables with sensible defaults.
No secrets or API keys are hard-coded.

"""

import os
from pathlib import Path

# Load backend/.env before reading os.getenv so .env values are available
# as defaults.  OS env vars already present take precedence.
_DOTENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if _DOTENV_PATH.exists():
    # python-dotenv does NOT override existing OS env vars by default
    from dotenv import load_dotenv
    load_dotenv(_DOTENV_PATH)


IMAGE_API_KEY: str = os.getenv("IMAGE_API_KEY", "")
IMAGE_API_BASE_URL: str = os.getenv("IMAGE_API_BASE_URL", "")

# --- Server -------------------------------------------------------------------
HOST: str = os.getenv("SPRITEFORGE_HOST", "0.0.0.0")
PORT: int = int(os.getenv("SPRITEFORGE_PORT", "8001"))


# --- Limits -------------------------------------------------------------------
MAX_GENERATE_COUNT: int = 16
MAX_PROMPT_LENGTH: int = 500
MAX_UPLOAD_SIZE_MB: int = 5

# --- CORS ---------------------------------------------------------------------
CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

"""
Application configuration.

All settings are read from environment variables with sensible defaults.
No secrets or API keys are hard-coded.

Load order:
  1. backend/.env  (via python-dotenv, if present)
  2. OS environment variables (take precedence over .env)
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

# --- Demo mode ---
DEMO_MODE: bool = os.getenv("DEMO_MODE", os.getenv("SPRITEFORGE_DEMO_MODE", "true")).lower() != "false"

# --- Image provider ---
# "demo"     → built-in sample assets
# "wanxiang" → Tongyi Wanxiang / DashScope text-to-image
IMAGE_PROVIDER: str = os.getenv("IMAGE_PROVIDER", "demo")

# --- DashScope / Tongyi Wanxiang ---
DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
WANXIANG_MODEL: str = os.getenv("WANXIANG_MODEL", "wan2.2-t2i-flash")
WANXIANG_SIZE: str = os.getenv("WANXIANG_SIZE", "1024*1024")
WANXIANG_N: int = int(os.getenv("WANXIANG_N", "1"))

# --- Fallback ---
ALLOW_DEMO_FALLBACK: bool = os.getenv("ALLOW_DEMO_FALLBACK", "true").lower() != "false"

# --- External AI API (legacy / generic) ---
IMAGE_API_KEY: str = os.getenv("IMAGE_API_KEY", "")
IMAGE_API_BASE_URL: str = os.getenv("IMAGE_API_BASE_URL", "")

# --- Server ---
HOST: str = os.getenv("SPRITEFORGE_HOST", "0.0.0.0")
PORT: int = int(os.getenv("SPRITEFORGE_PORT", "8000"))

# --- Paths ---
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR: str = os.path.join(BASE_DIR, "..", "output")
GENERATED_DIR: str = os.path.join(BASE_DIR, "..", "output", "generated")
SAMPLE_ASSETS_DIR: str = os.path.join(BASE_DIR, "..", "..", "examples", "sample-assets")

# --- Limits ---
MAX_GENERATE_COUNT: int = 16
MAX_PROMPT_LENGTH: int = 500
MAX_UPLOAD_SIZE_MB: int = 5

# --- CORS ---
CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

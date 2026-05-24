"""
Application configuration.

All settings are read from environment variables with sensible defaults.
No secrets or API keys are hard-coded.

Loads ``backend/.env`` via python-dotenv if available.
"""

import os

# --- Load .env file -----------------------------------------------------------
try:
    from dotenv import load_dotenv

    _ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    load_dotenv(_ENV_FILE)
except ImportError:  # pragma: no cover — python-dotenv not installed
    pass

# --- Demo mode ----------------------------------------------------------------
# DEMO_MODE takes priority; SPRITEFORGE_DEMO_MODE is a legacy alias.
_DM = os.getenv("DEMO_MODE") or os.getenv("SPRITEFORGE_DEMO_MODE") or "true"
DEMO_MODE: bool = _DM.lower() != "false"

# --- Image provider -----------------------------------------------------------
# "demo"     → built-in sample assets
# "wanxiang" → Tongyi Wanxiang / DashScope text-to-image
IMAGE_PROVIDER: str = os.getenv("IMAGE_PROVIDER", "demo")

# --- Tongyi Wanxiang / DashScope ----------------------------------------------
DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
WANXIANG_MODEL: str = os.getenv("WANXIANG_MODEL", "wanx-v1")
WANXIANG_SIZE: str = os.getenv("WANXIANG_SIZE", "1024*1024")
WANXIANG_N: int = int(os.getenv("WANXIANG_N", "1"))
ALLOW_DEMO_FALLBACK: bool = (
    os.getenv("ALLOW_DEMO_FALLBACK", "true").lower() != "false"
)

# --- External AI API (stub, kept for backwards compat) ------------------------
IMAGE_API_KEY: str = os.getenv("IMAGE_API_KEY", "")
IMAGE_API_BASE_URL: str = os.getenv("IMAGE_API_BASE_URL", "")

# --- Server -------------------------------------------------------------------
HOST: str = os.getenv("SPRITEFORGE_HOST", "0.0.0.0")
PORT: int = int(os.getenv("SPRITEFORGE_PORT", "8001"))

# --- Paths --------------------------------------------------------------------
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR: str = os.path.join(BASE_DIR, "..", "output")
SAMPLE_ASSETS_DIR: str = os.path.join(
    BASE_DIR, "..", "..", "examples", "sample-assets"
)
GENERATED_DIR: str = os.path.join(OUTPUT_DIR, "generated")

# --- Ensure runtime dirs exist ------------------------------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

# --- Limits -------------------------------------------------------------------
MAX_GENERATE_COUNT: int = 16
MAX_PROMPT_LENGTH: int = 500
MAX_UPLOAD_SIZE_MB: int = 5

# --- CORS ---------------------------------------------------------------------
CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

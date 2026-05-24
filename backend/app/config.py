"""
Application configuration.

All settings are read from environment variables with sensible defaults.
No secrets or API keys are hard-coded.
"""

import os

# Load .env file if present ------------------------------------------------
try:
    from dotenv import load_dotenv
    _ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    load_dotenv(_ENV_FILE)
except ImportError:
    pass

# --- Demo mode ------------------------------------------------------------
_DM = os.getenv("DEMO_MODE") or os.getenv("SPRITEFORGE_DEMO_MODE") or "true"
DEMO_MODE: bool = _DM.lower() != "false"

# --- Image provider -------------------------------------------------------
IMAGE_PROVIDER: str = os.getenv("IMAGE_PROVIDER", "demo")

# --- DashScope / Wanxiang ------------------------------------------------
DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
WANXIANG_MODEL: str = os.getenv("WANXIANG_MODEL", "wanx-v1")
WANXIANG_SIZE: str = os.getenv("WANXIANG_SIZE", "1024*1024")
WANXIANG_N: int = int(os.getenv("WANXIANG_N", "1"))

# --- Fallback -------------------------------------------------------------
ALLOW_DEMO_FALLBACK: bool = os.getenv("ALLOW_DEMO_FALLBACK", "true").lower() != "false"

# --- Server ---------------------------------------------------------------
HOST: str = os.getenv("SPRITEFORGE_HOST", "0.0.0.0")
PORT: int = int(os.getenv("SPRITEFORGE_PORT", "8001"))

# --- Paths ----------------------------------------------------------------
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR: str = os.path.join(BASE_DIR, "..", "output")
SAMPLE_ASSETS_DIR: str = os.path.join(BASE_DIR, "..", "..", "examples", "sample-assets")
GENERATED_DIR: str = os.path.join(OUTPUT_DIR, "generated")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

# --- Limits ---------------------------------------------------------------
MAX_GENERATE_COUNT: int = 16
MAX_PROMPT_LENGTH: int = 500
MAX_UPLOAD_SIZE_MB: int = 5

# --- Database --------------------------------------------------------------
DATABASE_PROVIDER: str = os.getenv("DATABASE_PROVIDER", "auto")
POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB: str = os.getenv("POSTGRES_DB", "spriteforge")
POSTGRES_USER: str = os.getenv("POSTGRES_USER", "spriteforge")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_SSLMODE: str = os.getenv("POSTGRES_SSLMODE", "disable")
SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", os.path.join(BASE_DIR, "..", "data", "spriteforge.db"))

# --- CORS -----------------------------------------------------------------
CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

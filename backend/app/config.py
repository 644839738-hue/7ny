"""
Application configuration.

All settings are read from environment variables with sensible defaults.
No secrets or API keys are hard-coded.
"""

import os

# --- Demo mode ---
# When True, the app uses built-in sample assets instead of calling an
# external AI API.  Controlled by SPRITEFORGE_DEMO_MODE env var.
DEMO_MODE: bool = os.getenv("SPRITEFORGE_DEMO_MODE", "true").lower() != "false"

# --- Server ---
HOST: str = os.getenv("SPRITEFORGE_HOST", "0.0.0.0")
PORT: int = int(os.getenv("SPRITEFORGE_PORT", "8000"))

# --- Paths ---
# Base directory of the backend package
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

# Directory for generated / processed output at runtime
OUTPUT_DIR: str = os.path.join(BASE_DIR, "..", "output")

# Directory containing sample assets for demo mode
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

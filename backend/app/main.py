"""
SpriteForge AI — FastAPI application entry point.

Start with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import CORS_ORIGINS, DEMO_MODE, GENERATED_DIR, OUTPUT_DIR
from app.routers import assets, export, generate, health, process, spritesheet, tile

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SpriteForge AI",
    description="2D game asset generation and processing pipeline",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health.router)
app.include_router(generate.router)
app.include_router(process.router)
app.include_router(spritesheet.router)
app.include_router(tile.router)
app.include_router(export.router)
app.include_router(assets.router)

# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup() -> None:
    """Ensure runtime directories and database exist."""
    import logging
    import os

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(GENERATED_DIR, exist_ok=True)

    from app.services.asset_repository import init_db
    from app.services.database import get_active_database_info

    init_db()

    db_info = get_active_database_info()
    logger = logging.getLogger("spriteforge")
    if db_info["provider"] == "postgres":
        logger.info("Database: PostgreSQL %s/%s%s",
                    db_info["host"], db_info["database"],
                    " (fallback)" if db_info["fallback"] else "")
    else:
        logger.info("Database: SQLite at %s%s",
                    db_info["path"],
                    " (fallback)" if db_info["fallback"] else "")


# Mount output so generated images are reachable via /output/<file>
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all for unhandled errors — returns structured JSON."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exc) if DEMO_MODE else "An unexpected error occurred.",
            }
        },
    )

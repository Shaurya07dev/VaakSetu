"""
VaakSetu Backend — FastAPI Application

Entry point: python -m uvicorn task2_backend.main:app --port 8000 --reload
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from task2_backend.database import init_db
from task2_backend.routes_agents import router as agents_router
from task2_backend.routes_sessions import router as sessions_router
from task2_backend.routes_streams import router as streams_router
from task2_backend.routes_calls import router as calls_router
from task2_backend.routes_twilio_media import router as twilio_media_router
from task2_backend.routes_live_mic import router as live_mic_router

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("vaaksetu.backend")


# ── Lifespan ───────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    logger.info("=" * 60)
    logger.info("VaakSetu Backend — Starting up...")
    logger.info("=" * 60)

    # Initialize database
    await init_db()
    logger.info("✓ Database initialized (SQLite)")

    # Load domain configs for legacy support
    try:
        from task1_ai_core.config import CONFIGS_DIR
        configs = list(CONFIGS_DIR.glob("*.yaml"))
        logger.info(f"✓ Domain configs loaded ({', '.join(c.stem for c in configs)})")
    except Exception as e:
        logger.warning(f"✗ Domain config loading failed: {e}")

    # Validate Twilio config
    try:
        from task1_ai_core.twilio_config import validate_twilio_config
        tw_issues = validate_twilio_config()
        if tw_issues:
            for w in tw_issues:
                logger.warning(f"✗ Twilio: {w}")
        else:
            logger.info("✓ Twilio config validated")
    except Exception as e:
        logger.warning(f"✗ Twilio config check failed: {e}")

    logger.info("✓ Live Conversation UI at http://localhost:8000/live")
    logger.info("✓ Backend ready on http://localhost:8000")
    logger.info("=" * 60)

    yield

    logger.info("VaakSetu Backend — Shutting down...")


# ── App ────────────────────────────────────────────────────────
app = FastAPI(
    title="VaakSetu API",
    description="AI-Powered Multilingual Conversational Intelligence Platform",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(agents_router)
app.include_router(sessions_router)
app.include_router(streams_router)
app.include_router(calls_router)
app.include_router(twilio_media_router)
app.include_router(live_mic_router)

# Serve the static UI files
_static_dir = Path(__file__).parent / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


@app.get("/")
async def root():
    return {
        "service": "VaakSetu API",
        "version": "2.0.0",
        "status": "operational",
        "live_ui": "/live",
    }


@app.get("/live")
async def live_ui():
    """Serve the live conversation recording UI."""
    html_path = Path(__file__).parent / "static" / "live.html"
    return FileResponse(str(html_path), media_type="text/html")


@app.get("/health")
async def health():
    return {"status": "healthy"}

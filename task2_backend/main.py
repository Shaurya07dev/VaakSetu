"""
VaakSetu Backend — FastAPI Application

Entry point: python -m uvicorn task2_backend.main:app --port 8000 --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from task2_backend.database import init_db
from task2_backend.routes_agents import router as agents_router
from task2_backend.routes_sessions import router as sessions_router

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


@app.get("/")
async def root():
    return {
        "service": "VaakSetu API",
        "version": "2.0.0",
        "status": "operational",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}

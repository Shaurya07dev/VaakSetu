"""
VaakSetu Backend — Session & Conversation Routes

Endpoints:
  POST  /api/sessions                — Start a new session for an agent
  POST  /api/sessions/{id}/message   — Send a message and get AI response
  GET   /api/sessions/{id}           — Get full session state + messages
  POST  /api/sessions/{id}/end       — End session, trigger scoring
  POST  /api/transcribe              — ASR: audio bytes → text
"""

import uuid
import logging
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from task2_backend.database import (
    get_agent,
    create_session,
    get_session,
    update_session,
    add_message,
    get_messages,
)

logger = logging.getLogger("vaaksetu.routes.sessions")
router = APIRouter(prefix="/api", tags=["sessions"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Request Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class StartSessionRequest(BaseModel):
    agent_id: str


class SendMessageRequest(BaseModel):
    content: str
    input_type: str = "text"  # "text" or "voice"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Lazy-loaded AI components (avoid import-time failures)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_smart_agent = None
_asr_pipeline = None
_reward_engine = None


def _get_agent():
    """Lazy-init the SmartDialogueAgent."""
    global _smart_agent
    if _smart_agent is None:
        from task1_ai_core.agent import SmartDialogueAgent
        _smart_agent = SmartDialogueAgent()
    return _smart_agent


def _get_asr():
    """Lazy-init the ASR pipeline."""
    global _asr_pipeline
    if _asr_pipeline is None:
        from task1_ai_core.asr import ASRPipeline
        _asr_pipeline = ASRPipeline()
    return _asr_pipeline


def _get_reward():
    """Lazy-init the reward engine."""
    global _reward_engine
    if _reward_engine is None:
        from task1_ai_core.reward_engine import RewardEngine
        _reward_engine = RewardEngine()
    return _reward_engine


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Routes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/sessions")
async def api_start_session(req: StartSessionRequest):
    """Start a new conversation session for an agent."""
    agent = await get_agent(req.agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    session_id = f"s-{uuid.uuid4().hex[:8]}"

    # Create session in DB
    session = await create_session(session_id, req.agent_id)

    # Build agent config and start the AI session
    smart_agent = _get_agent()
    greeting_response = await smart_agent.start_session(
        session_id=session_id,
        agent_config=agent,
    )

    # Save greeting as first message
    await add_message(session_id, "assistant", greeting_response.response, turn_number=0)

    logger.info(f"Session started: {session_id} for agent {req.agent_id}")
    return {
        "status": "ok",
        "session_id": session_id,
        "greeting": greeting_response.response,
        "missing_fields": greeting_response.missing_fields,
        "agent": agent,
    }


@router.post("/sessions/{session_id}/message")
async def api_send_message(session_id: str, req: SendMessageRequest):
    """Send a user message and get AI response."""
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="Session is no longer active")

    agent = await get_agent(session["agent_id"])
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Increment turn count
    turn = session["turn_count"] + 1

    # Save user message
    await add_message(session_id, "user", req.content, turn_number=turn)

    # Get AI response
    smart_agent = _get_agent()
    response = await smart_agent.respond(
        session_id=session_id,
        user_input=req.content,
        agent_config=agent,
    )

    # Save assistant message
    await add_message(session_id, "assistant", response.response, turn_number=turn)

    # Update session state
    await update_session(
        session_id,
        collected_fields=response.collected_fields,
        is_complete=response.is_complete,
        turn_count=turn,
    )

    logger.info(
        f"Session {session_id} turn {turn}: "
        f"collected={list(response.collected_fields.keys())}, "
        f"complete={response.is_complete}"
    )

    return {
        "status": "ok",
        "response": response.response,
        "collected_fields": response.collected_fields,
        "missing_fields": response.missing_fields,
        "is_complete": response.is_complete,
        "is_escalation": response.is_escalation,
        "turn_number": turn,
    }


@router.get("/sessions/{session_id}")
async def api_get_session(session_id: str):
    """Get full session data including messages."""
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await get_messages(session_id)
    agent = await get_agent(session["agent_id"])

    return {
        "status": "ok",
        "session": session,
        "messages": messages,
        "agent": agent,
    }


@router.post("/sessions/{session_id}/end")
async def api_end_session(session_id: str):
    """End a session and trigger RLAIF scoring."""
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await get_messages(session_id)
    agent = await get_agent(session["agent_id"])
    now = datetime.now(timezone.utc).isoformat()

    # Run RLAIF scoring
    reward_scores = None
    try:
        from task1_ai_core.reward_engine import RewardEngine, ConversationTurn
        engine = _get_reward()

        turns = [
            ConversationTurn(
                role=m["role"],
                content=m["content"],
                sentiment_score=0.5,  # Simplified — could add real sentiment
                turn_number=m["turn_number"],
            )
            for m in messages
        ]

        if turns:
            result = await engine.score(
                turns,
                domain=agent["domain"] if agent else "general",
                is_complete=session["is_complete"],
            )
            reward_scores = result.model_dump()
            logger.info(f"Session {session_id} scored: {result.combined_reward:.3f} ({result.dpo_label})")
    except Exception as e:
        logger.warning(f"RLAIF scoring failed for {session_id}: {e}")
        reward_scores = {"error": str(e)}

    # Update session as ended
    await update_session(
        session_id,
        status="completed",
        ended_at=now,
        reward_scores=reward_scores,
    )

    return {
        "status": "ok",
        "session": await get_session(session_id),
        "messages": messages,
        "reward_scores": reward_scores,
        "agent": agent,
    }


@router.post("/transcribe")
async def api_transcribe(audio: UploadFile = File(...)):
    """Transcribe audio to text using the ASR pipeline."""
    try:
        asr = _get_asr()
        audio_bytes = await audio.read()

        # Determine format from filename
        ext = Path(audio.filename or "audio.webm").suffix.lstrip(".")
        if ext not in ("wav", "mp3", "webm", "ogg", "m4a"):
            ext = "webm"  # Default for MediaRecorder

        result = await asr.transcribe_bytes(audio_bytes, file_format=ext)

        return {
            "status": "ok",
            "transcript": result.transcript,
            "language_code": result.language_code,
            "confidence": result.confidence,
            "source": result.source,
        }
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

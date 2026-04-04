"""
VaakSetu — Live Microphone WebSocket Handler

Accepts audio blobs from the browser MediaRecorder API,
runs ASR on each chunk, feeds the LangGraph agent,
and streams transcript + narrative updates back to the UI.
"""

import asyncio
import base64
import json
import logging
import tempfile
import uuid
from collections import defaultdict
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("vaaksetu.live_mic")
router = APIRouter(prefix="/api/live", tags=["Live Microphone"])

# Per-session state
_sessions: dict[str, dict] = {}


def _get_session(session_id: str, domain: str = "healthcare") -> dict:
    if session_id not in _sessions:
        _sessions[session_id] = {
            "session_id": session_id,
            "domain": domain,
            "transcript_chunks": [],
            "narrative": "",
            "structured_data": {},
            "speaker_map": {},
            "is_recording": True,
        }
    return _sessions[session_id]


@router.websocket("/stream")
async def live_mic_stream(websocket: WebSocket):
    """
    WebSocket for live microphone streaming.
    
    Protocol:
      Client → Server (JSON):
        {"type": "start", "domain": "healthcare"}
        {"type": "audio", "data": "<base64-wav-bytes>"}
        {"type": "stop"}
        
      Server → Client (JSON):
        {"type": "session_started", "session_id": "..."}
        {"type": "transcript", "text": "...", "chunk_index": N}
        {"type": "narrative", "text": "..."}
        {"type": "structured_data", "data": {...}}
        {"type": "speaker_map", "data": {...}}
        {"type": "summary_complete", "transcript": [...], "narrative": "...", "structured_data": {...}}
        {"type": "error", "message": "..."}
    """
    await websocket.accept()
    session_id = f"live-{uuid.uuid4().hex[:8]}"
    session = None
    
    logger.info(f"Live mic WebSocket connected: {session_id}")

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            msg_type = msg.get("type", "")

            if msg_type == "start":
                domain = msg.get("domain", "healthcare")
                session = _get_session(session_id, domain)
                await websocket.send_text(json.dumps({
                    "type": "session_started",
                    "session_id": session_id,
                }))
                logger.info(f"[{session_id}] Recording started, domain={domain}")

            elif msg_type == "audio":
                if not session:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Session not started. Send {'type': 'start'} first."
                    }))
                    continue

                audio_b64 = msg.get("data", "")
                if not audio_b64:
                    continue

                audio_bytes = base64.b64decode(audio_b64)
                chunk_index = len(session["transcript_chunks"])

                # Write to temp file for ASR
                with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
                    tmp.write(audio_bytes)
                    tmp_path = tmp.name

                try:
                    # Run ASR
                    from task1_ai_core.asr import ASRPipeline
                    pipeline = ASRPipeline()
                    result = await pipeline.transcribe(tmp_path)
                    transcript_text = result.transcript.strip()
                finally:
                    Path(tmp_path).unlink(missing_ok=True)

                if not transcript_text:
                    logger.info(f"[{session_id}] Chunk {chunk_index}: silence/empty")
                    continue

                session["transcript_chunks"].append(transcript_text)
                logger.info(f"[{session_id}] Chunk {chunk_index}: '{transcript_text[:60]}...'")

                # Send transcript update immediately
                await websocket.send_text(json.dumps({
                    "type": "transcript",
                    "text": transcript_text,
                    "chunk_index": chunk_index,
                }))

                # Feed into LangGraph agent
                try:
                    from task1_ai_core.conversation_processor import StreamConversationProcessor
                    processor = StreamConversationProcessor()
                    graph_result = await processor.ingest_chunk(
                        session_id, session["domain"], transcript_text
                    )

                    if graph_result.get("status") == "success":
                        narrative = graph_result.get("narrative", "")
                        structured = graph_result.get("structured_data", {})
                        speakers = graph_result.get("speaker_map", {})

                        session["narrative"] = narrative
                        session["structured_data"] = structured
                        session["speaker_map"] = speakers

                        await websocket.send_text(json.dumps({
                            "type": "narrative",
                            "text": narrative,
                        }))
                        await websocket.send_text(json.dumps({
                            "type": "structured_data",
                            "data": structured,
                        }))
                        if speakers:
                            await websocket.send_text(json.dumps({
                                "type": "speaker_map",
                                "data": speakers,
                            }))
                except Exception as e:
                    logger.error(f"[{session_id}] Graph agent error: {e}")

            elif msg_type == "stop":
                logger.info(f"[{session_id}] Recording stopped by client")
                if session:
                    session["is_recording"] = False
                    await websocket.send_text(json.dumps({
                        "type": "summary_complete",
                        "transcript": session["transcript_chunks"],
                        "narrative": session["narrative"],
                        "structured_data": session["structured_data"],
                        "speaker_map": session["speaker_map"],
                    }))
                break

    except WebSocketDisconnect:
        logger.info(f"[{session_id}] Client disconnected")
    except Exception as e:
        logger.error(f"[{session_id}] WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass

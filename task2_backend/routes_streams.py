import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict

from task1_ai_core.conversation_processor import StreamConversationProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["RealTime Call Summarization"])

# Global processor instance
stream_processor = StreamConversationProcessor()

class ConnectionManager:
    """Manages active WS connections for call streaming."""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()


@router.websocket("/{session_id}/stream")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for live real-time ingestion.
    Expects JSON text payloads from the frontend.
    For audio chunks, a proper VAD/ASR step would precede the ingestion in production, 
    but for this logical layer we ingest recognized transcript text chunks.
    """
    await manager.connect(session_id, websocket)
    logger.info(f"Session {session_id} connected to real-time WS streaming.")
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            domain = payload.get("domain", "general")
            transcript_chunk = payload.get("transcript_chunk", "")

            # Push chunk into graph agent pipeline
            result = await stream_processor.ingest_chunk(session_id, domain, transcript_chunk)

            # Transmit updates downstream to the client (UI rendering)
            if result.get("status") == "success":
                await manager.send_personal_message(
                    json.dumps({
                        "type": "agent_update",
                        "narrative": result.get("narrative"),
                        "structured_data": result.get("structured_data"),
                        "speaker_map": result.get("speaker_map")
                    }),
                    session_id
                )
            else:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": result.get("error", "Unknown ingestion error")}),
                    session_id
                )
    except WebSocketDisconnect:
        logger.info(f"Session {session_id} disconnected.")
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket execution error: {e}")
        manager.disconnect(session_id)

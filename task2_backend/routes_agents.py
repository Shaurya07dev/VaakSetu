"""
VaakSetu Backend — Agent CRUD Routes

Endpoints:
  POST   /api/agents       — Create a new agent
  GET    /api/agents        — List all agents
  GET    /api/agents/{id}   — Get single agent
  PUT    /api/agents/{id}   — Update agent
  DELETE /api/agents/{id}   — Delete agent
"""

import uuid
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from task2_backend.database import (
    create_agent,
    get_agent,
    list_agents,
    update_agent,
    delete_agent,
)

logger = logging.getLogger("vaaksetu.routes.agents")
router = APIRouter(prefix="/api/agents", tags=["agents"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Request / Response Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AgentCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    domain: str = Field(min_length=1)
    customDomain: Optional[str] = ""
    inputs: list[str] = ["Voice"]
    fields: list[str] = []
    prompt: Optional[str] = ""
    greeting: Optional[str] = ""
    triggers: list[str] = []
    escalation: dict = {}
    escalation_message: Optional[str] = ""
    default_language: Optional[str] = "hi-IN"


class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    customDomain: Optional[str] = None
    inputs: Optional[list[str]] = None
    fields: Optional[list[str]] = None
    prompt: Optional[str] = None
    greeting: Optional[str] = None
    triggers: Optional[list[str]] = None
    escalation: Optional[dict] = None
    escalation_message: Optional[str] = None
    default_language: Optional[str] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Routes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("")
async def api_create_agent(req: AgentCreateRequest):
    """Create a new agent from the frontend wizard form."""
    agent_id = str(uuid.uuid4())[:8]
    agent_data = req.model_dump()
    agent_data["id"] = agent_id

    # Auto-generate greeting if not provided
    if not agent_data.get("greeting"):
        display_domain = agent_data.get("customDomain") or agent_data["domain"]
        agent_data["greeting"] = (
            f"Namaste! Main {agent_data['name']} hoon. "
            f"Aaj main aapki {display_domain} se related madad karunga. "
            f"Kya aap shuru karein?"
        )

    agent = await create_agent(agent_data)
    logger.info(f"Agent created: {agent_id} ({agent_data['name']})")
    return {"status": "ok", "agent": agent}


@router.get("")
async def api_list_agents():
    """List all agents."""
    agents = await list_agents()
    return {"status": "ok", "agents": agents}


@router.get("/{agent_id}")
async def api_get_agent(agent_id: str):
    """Get a single agent by ID."""
    agent = await get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "ok", "agent": agent}


@router.put("/{agent_id}")
async def api_update_agent(agent_id: str, req: AgentUpdateRequest):
    """Update an existing agent."""
    existing = await get_agent(agent_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Merge: only update fields that were provided
    update_data = existing.copy()
    for key, val in req.model_dump(exclude_none=True).items():
        update_data[key] = val

    agent = await update_agent(agent_id, update_data)
    logger.info(f"Agent updated: {agent_id}")
    return {"status": "ok", "agent": agent}


@router.delete("/{agent_id}")
async def api_delete_agent(agent_id: str):
    """Delete an agent and all its sessions."""
    deleted = await delete_agent(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    logger.info(f"Agent deleted: {agent_id}")
    return {"status": "ok", "message": "Agent deleted"}

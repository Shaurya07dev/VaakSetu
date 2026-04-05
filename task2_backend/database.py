"""
VaakSetu Backend — SQLite Database Layer

Uses aiosqlite for async access. Tables:
  • agents           — Dynamic agent configurations (replaces static YAML)
  • sessions         — Conversation sessions tied to agents
  • messages         — Individual messages in each session
  • extracted_fields — Structured data extracted per session
"""

import aiosqlite
import json
import os
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger("vaaksetu.database")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "vaaksetu.db"


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS agents (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    domain          TEXT NOT NULL,
    custom_domain   TEXT DEFAULT '',
    inputs          TEXT DEFAULT '["Voice"]',
    fields          TEXT DEFAULT '[]',
    system_prompt   TEXT DEFAULT '',
    greeting        TEXT DEFAULT '',
    triggers        TEXT DEFAULT '[]',
    escalation      TEXT DEFAULT '{}',
    escalation_message TEXT DEFAULT '',
    default_language TEXT DEFAULT 'hi-IN',
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id              TEXT PRIMARY KEY,
    agent_id        TEXT NOT NULL,
    status          TEXT DEFAULT 'active',
    collected_fields TEXT DEFAULT '{}',
    is_complete     INTEGER DEFAULT 0,
    turn_count      INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL,
    ended_at        TEXT,
    reward_scores   TEXT,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    role            TEXT NOT NULL,
    content         TEXT NOT NULL,
    turn_number     INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_agent ON sessions(agent_id);
"""


async def get_db() -> aiosqlite.Connection:
    """Get a database connection with row factory enabled."""
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Initialize the database schema."""
    db = await get_db()
    try:
        await db.executescript(SCHEMA_SQL)
        await db.commit()
        logger.info(f"Database initialized at {DB_PATH}")
    finally:
        await db.close()


async def close_db(db: aiosqlite.Connection):
    """Close a database connection."""
    await db.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Agent CRUD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def create_agent(agent_data: dict) -> dict:
    """Insert a new agent into the database."""
    db = await get_db()
    try:
        now = datetime.now(timezone.utc).isoformat()
        await db.execute(
            """INSERT INTO agents (id, name, domain, custom_domain, inputs, fields,
               system_prompt, greeting, triggers, escalation, escalation_message,
               default_language, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                agent_data["id"],
                agent_data["name"],
                agent_data["domain"],
                agent_data.get("customDomain", ""),
                json.dumps(agent_data.get("inputs", ["Voice"])),
                json.dumps(agent_data.get("fields", [])),
                agent_data.get("prompt", ""),
                agent_data.get("greeting", ""),
                json.dumps(agent_data.get("triggers", [])),
                json.dumps(agent_data.get("escalation", {})),
                agent_data.get("escalation_message", ""),
                agent_data.get("default_language", "hi-IN"),
                now,
                now,
            ),
        )
        await db.commit()
        return await get_agent(agent_data["id"])
    finally:
        await db.close()


async def get_agent(agent_id: str) -> dict | None:
    """Fetch a single agent by ID."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        return _row_to_agent(row)
    finally:
        await db.close()


async def list_agents() -> list[dict]:
    """List all agents ordered by creation date (newest first)."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM agents ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [_row_to_agent(r) for r in rows]
    finally:
        await db.close()


async def update_agent(agent_id: str, agent_data: dict) -> dict | None:
    """Update an existing agent."""
    db = await get_db()
    try:
        now = datetime.now(timezone.utc).isoformat()
        await db.execute(
            """UPDATE agents SET name=?, domain=?, custom_domain=?, inputs=?, fields=?,
               system_prompt=?, greeting=?, triggers=?, escalation=?, escalation_message=?,
               default_language=?, updated_at=?
               WHERE id=?""",
            (
                agent_data["name"],
                agent_data["domain"],
                agent_data.get("customDomain", ""),
                json.dumps(agent_data.get("inputs", ["Voice"])),
                json.dumps(agent_data.get("fields", [])),
                agent_data.get("prompt", ""),
                agent_data.get("greeting", ""),
                json.dumps(agent_data.get("triggers", [])),
                json.dumps(agent_data.get("escalation", {})),
                agent_data.get("escalation_message", ""),
                agent_data.get("default_language", "hi-IN"),
                now,
                agent_id,
            ),
        )
        await db.commit()
        return await get_agent(agent_id)
    finally:
        await db.close()


async def delete_agent(agent_id: str) -> bool:
    """Delete an agent and its sessions/messages."""
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


def _row_to_agent(row) -> dict:
    """Convert a database row to an agent dict."""
    return {
        "id": row["id"],
        "name": row["name"],
        "domain": row["domain"],
        "customDomain": row["custom_domain"],
        "inputs": json.loads(row["inputs"]),
        "fields": json.loads(row["fields"]),
        "prompt": row["system_prompt"],
        "greeting": row["greeting"],
        "triggers": json.loads(row["triggers"]),
        "escalation": json.loads(row["escalation"]),
        "escalation_message": row["escalation_message"],
        "default_language": row["default_language"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Session CRUD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def create_session(session_id: str, agent_id: str) -> dict:
    """Create a new conversation session."""
    db = await get_db()
    try:
        now = datetime.now(timezone.utc).isoformat()
        await db.execute(
            """INSERT INTO sessions (id, agent_id, status, collected_fields,
               is_complete, turn_count, created_at)
               VALUES (?, ?, 'active', '{}', 0, 0, ?)""",
            (session_id, agent_id, now),
        )
        await db.commit()
        return await get_session(session_id)
    finally:
        await db.close()


async def get_session(session_id: str) -> dict | None:
    """Fetch a session by ID."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        return _row_to_session(row)
    finally:
        await db.close()


async def update_session(session_id: str, **kwargs) -> dict | None:
    """Update session fields dynamically."""
    db = await get_db()
    try:
        sets = []
        values = []
        for key, val in kwargs.items():
            if key == "collected_fields":
                sets.append("collected_fields = ?")
                values.append(json.dumps(val))
            elif key == "is_complete":
                sets.append("is_complete = ?")
                values.append(1 if val else 0)
            elif key == "turn_count":
                sets.append("turn_count = ?")
                values.append(val)
            elif key == "status":
                sets.append("status = ?")
                values.append(val)
            elif key == "ended_at":
                sets.append("ended_at = ?")
                values.append(val)
            elif key == "reward_scores":
                sets.append("reward_scores = ?")
                values.append(json.dumps(val))

        if not sets:
            return await get_session(session_id)

        values.append(session_id)
        await db.execute(
            f"UPDATE sessions SET {', '.join(sets)} WHERE id = ?",
            values,
        )
        await db.commit()
        return await get_session(session_id)
    finally:
        await db.close()


async def get_sessions_for_agent(agent_id: str) -> list[dict]:
    """List all sessions for an agent."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM sessions WHERE agent_id = ? ORDER BY created_at DESC",
            (agent_id,),
        )
        rows = await cursor.fetchall()
        return [_row_to_session(r) for r in rows]
    finally:
        await db.close()


async def list_sessions() -> list[dict]:
    """List all sessions ordered by creation date (newest first)."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM sessions ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [_row_to_session(r) for r in rows]
    finally:
        await db.close()


async def delete_session(session_id: str) -> bool:
    """Delete a session and all of its messages."""
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


def _row_to_session(row) -> dict:
    """Convert a database row to a session dict."""
    return {
        "id": row["id"],
        "agent_id": row["agent_id"],
        "status": row["status"],
        "collected_fields": json.loads(row["collected_fields"]),
        "is_complete": bool(row["is_complete"]),
        "turn_count": row["turn_count"],
        "created_at": row["created_at"],
        "ended_at": row["ended_at"],
        "reward_scores": json.loads(row["reward_scores"]) if row["reward_scores"] else None,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Message CRUD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def add_message(session_id: str, role: str, content: str, turn_number: int) -> dict:
    """Add a message to a session."""
    db = await get_db()
    try:
        now = datetime.now(timezone.utc).isoformat()
        cursor = await db.execute(
            """INSERT INTO messages (session_id, role, content, turn_number, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, role, content, turn_number, now),
        )
        await db.commit()
        return {
            "id": cursor.lastrowid,
            "session_id": session_id,
            "role": role,
            "content": content,
            "turn_number": turn_number,
            "created_at": now,
        }
    finally:
        await db.close()


async def get_messages(session_id: str) -> list[dict]:
    """Get all messages for a session ordered by turn number."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY turn_number ASC, id ASC",
            (session_id,),
        )
        rows = await cursor.fetchall()
        return [
            {
                "id": r["id"],
                "session_id": r["session_id"],
                "role": r["role"],
                "content": r["content"],
                "turn_number": r["turn_number"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    finally:
        await db.close()

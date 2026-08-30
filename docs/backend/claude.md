# CLAUDE.md

Persistent rules for this repository. Read `docs/MASTER_PLAN.md` for the task graph.
This file is loaded on every session. Keep it under 300 lines — it competes for context with real work.

---

## What this is

A multi-tenant conversational intelligence platform. One backend serves three surfaces:

- **Personal recorder** — mobile app records conversations/meetings, gets summaries
- **Client agent** — configurable receptionist / kiosk / role assistant for hospitals, banks, hotels
- **Calling agent** — outbound & inbound phone agent that talks, acts, and summarises

**They are the same primitive.** A `Session` varies by `mode` (`OBSERVE` / `RESPOND` / `DRIVE`) and `channel` (ingress adapter). If a feature request seems to need a new service per vertical, it doesn't — it needs a config field. Say so instead of building it.

---

## Non-negotiable invariants

Violating any of these is a bug even if tests pass.

1. **`session_events` is append-only.** No UPDATE, no DELETE in application code. Everything else (`turns`, `records`, `narratives`) is a projection rebuildable from it.
2. **Every table with tenant data has `tenant_id` NOT NULL** and is covered by row-level security. Never filter by tenant in Python only.
3. **The media path never blocks on an LLM or TTS call.** `media_gateway` and `agent_runtime` communicate over the bus, never by direct await on inference.
4. **All ingress normalises to PCM16 / 16 kHz / mono / 20 ms frames** before leaving the adapter. No provider-specific format (mulaw, Opus, WebM) exists above `app/ingress/`.
5. **No fixed-size audio buffering in `RESPOND` or `DRIVE` mode.** Turn boundaries come from VAD endpointing. Fixed buffers are permitted only in `OBSERVE`.
6. **Structured extraction uses schema-constrained decoding.** Never `json.loads()` a free-form LLM response into a `Record`.
7. **Side effects run in `action_service` with an idempotency key.** `agent_runtime` returns *intent to act*; it never performs the write itself.
8. **Personas are immutable once published.** Edits create a new version. Sessions pin `persona_version` at creation.
9. **No PII in `session_events.payload`.** Store a reference to an encrypted column instead. We must be able to honour erasure requests without rewriting the event log.
10. **Telephony webhooks validate the provider signature before any processing.** Unsigned request → 403, no logging of body.
11. **Speech is untrusted input.** Tool arguments derived from a caller's words are schema-validated, and irreversible actions require confirmation. A caller must never be able to talk the agent into an unapproved tool call.
12. **Every AI-generated field carries `source_turn_id`.** A field with no source span is a hallucination and must be dropped, not stored.

---

## Stack (pinned — do not substitute)

| Layer | Choice | Note |
|---|---|---|
| Python | **3.12** | NOT 3.13 — `audioop` was removed in 3.13 and telephony audio conversion needs it |
| Package manager | `uv` | `uv sync`, `uv run` |
| Web | FastAPI + Uvicorn | |
| Validation | Pydantic v2 | |
| ORM | SQLAlchemy 2.0 async + Alembic | Async everywhere; no sync sessions |
| DB | Postgres 16 + pgvector | |
| Cache / live state | Redis 7 | |
| Bus | Redis Streams behind `EventBus` protocol | NATS swap later; keep the interface clean |
| Object store | S3 API (MinIO locally) via `boto3` | |
| Test | pytest + pytest-asyncio + testcontainers | |
| Lint/format/type | ruff + mypy (strict on `app/core`, `app/agent`) | |

---

## Repo layout

```
app/
  core/            # domain model, state machines, protocols. ZERO external I/O.
    session.py     # Session aggregate + state machine
    events.py      # event types
    persona.py     # Persona spec model + validation
    protocols.py   # ASRProvider, LLMProvider, TTSProvider, EventBus, IngressAdapter...
  api/             # FastAPI routers. Thin — parse, authorise, delegate.
    v1/
  services/
    session_service.py
    agent_runtime/       # dialogue policy, slot filling, turn decisions
    action_service/      # tool execution, idempotency, approvals
    intelligence/        # async pipeline: diarise, extract, narrate, embed
  ingress/         # one module per channel; each implements IngressAdapter
    mobile.py  meeting.py  telephony/  kiosk.py  text.py
  media/           # VAD, endpointing, resampling, framing, jitter buffer
  inference/       # provider adapters + fallback chains + budgets
    asr/  llm/  tts/  embed/
  infra/           # db, redis, s3, bus, kms, logging, config
  workers/         # queue consumers
tests/
  unit/  integration/  eval/
docs/
  MASTER_PLAN.md   # task graph — the build order
  contracts/       # OpenAPI, JSON schemas, persona schema
migrations/
```

**Dependency rule:** `core` imports nothing from `app.*` except `core`. `api` never imports `inference` directly. If you need an import that breaks this, the design is wrong — stop and flag it.

---

## Conventions

- **Async by default.** Any function touching I/O is `async def`. No `requests`, no sync DB sessions.
- **Errors:** raise typed exceptions from `app/core/errors.py`. API layer maps them to HTTP. Never return `{"error": ...}` from a service.
- **Logging:** `structlog`, JSON, always bind `session_id` and `tenant_id`. Never log transcript text, phone numbers, or names at INFO. Redact at the logger, not the call site.
- **Config:** Pydantic `Settings` from env. No `os.getenv` scattered in modules. No secrets in persona configs — only secret-store references.
- **Time:** UTC, timezone-aware, always. Durations in the domain are `_ms` ints.
- **Money/cost:** integer cents/paise. No floats.
- **IDs:** UUIDv7 for everything (sortable). `session_id` is the correlation ID across all logs, traces and bus messages.
- **Migrations:** every schema change is an Alembic migration. Never `create_all()` outside tests.
- **Tests:** every task ships tests in the same commit. Integration tests use testcontainers, not mocks, for Postgres and Redis. Mock only external paid APIs.

---

## Commands

```bash
uv sync                                  # install
docker compose up -d postgres redis minio
uv run alembic upgrade head              # migrate
uv run uvicorn app.main:app --reload     # serve
uv run pytest -q                         # all tests
uv run pytest tests/unit -q              # fast loop
uv run ruff check . && uv run ruff format --check .
uv run mypy app/core app/agent
make verify                              # lint + type + test — MUST pass before "done"
```

---

## How to work here

- **One task from `docs/MASTER_PLAN.md` at a time.** Each task lists files, contract, and acceptance criteria. Do not start the next task before `make verify` passes.
- **Read the contract before writing code.** If `docs/contracts/` has a schema for what you're building, it wins over your intuition.
- **Stubs are allowed at boundaries, never in the middle.** A provider adapter may raise `NotImplementedError` if its task hasn't run yet. Core logic may not.
- **When a decision is marked OPEN in the master plan, do not silently pick one.** Implement behind the protocol, use the simplest option, and note the choice in `docs/decisions.md`.
- **If a requirement contradicts an invariant above, stop and say so.** Do not work around it.

---

## Do not

- Do not add a new top-level service without an explicit instruction.
- Do not upsample 8 kHz telephony audio to 16 kHz "for quality" — it adds no information. Only convert when a downstream model hard-requires 16 kHz, and say so in a comment.
- Do not put retry logic in `agent_runtime`. Retries belong to `action_service` and `inference`.
- Do not cache LLM responses keyed on transcript text (PII in cache keys).
- Do not use one model for everything — see the tiering table in the master plan.
- Do not write a "utils.py". Name modules for what they own.
- Do not commit `.env`, fixtures with real audio of real people, or provider credentials.
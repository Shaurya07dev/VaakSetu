# MASTER_PLAN.md — Backend Build Specification

**Consumer:** Claude Code. This is a task graph, not a whitepaper.
**Rules of engagement:** see `CLAUDE.md` (invariants, stack, conventions). Those override anything here.

---

## 0. Orientation (read once per session)

One backend, three surfaces, one primitive.

```
Session = (mode, channel, persona) → Transcript + Record + Narrative + Actions

mode     OBSERVE  agent listens only          → recorder, meeting capture, call co-pilot
         RESPOND  agent listens + speaks + acts → receptionist, kiosk, inbound support
         DRIVE    agent leads the conversation  → outbound sales / collections

channel  MOBILE_MIC | MEETING_BOT | PSTN_IN | PSTN_OUT | KIOSK | TEXT
```

Everything customisable about a client deployment lives in a **Persona** document (§3). Adding a hospital, a bank or a hotel must never require new services.

**Data flow, live path:**
```
ingress adapter → media (VAD, endpoint) → inference.asr → bus
                                                            ↓
                                          agent_runtime (turn decision)
                                            ↓                    ↓
                                   inference.tts → egress    action_service
```

**Data flow, async path:**
```
session.ended → workers → diarise → reconcile transcript → extract (schema-constrained)
              → narrate → embed → score → webhook to tenant
```

---

## 1. Task graph

Tasks are dependency-ordered. **Do one at a time.** Each ends with `make verify` green.
`⊣` = depends on.

### Phase 0 — Skeleton (no audio)

Goal: a typed conversation produces a structured record and a narrative. Proves the intelligence layer before any real-time risk.

---

#### T01 — Project scaffold
**Files:** `pyproject.toml`, `Makefile`, `docker-compose.yml`, `app/main.py`, `app/infra/config.py`, `app/infra/logging.py`, `app/core/errors.py`
**Do:** uv project on Python 3.12. FastAPI app with `/healthz` (liveness) and `/readyz` (checks Postgres + Redis). structlog JSON logging with `session_id`/`tenant_id` binding and a PII redaction processor. Pydantic `Settings`. docker-compose with postgres:16 (pgvector image), redis:7, minio. `make verify` = ruff + mypy + pytest.
**Accept:** `docker compose up -d && uv run uvicorn app.main:app` → `/readyz` returns 200 with both dependencies healthy; returns 503 when Postgres is stopped. `make verify` passes on an empty test suite.

---

#### T02 — Domain model & protocols ⊣ T01
**Files:** `app/core/session.py`, `app/core/events.py`, `app/core/persona.py`, `app/core/protocols.py`
**Do:** Pure Python, zero I/O. Define:

```python
class SessionMode(StrEnum): OBSERVE; RESPOND; DRIVE
class Channel(StrEnum): MOBILE_MIC; MEETING_BOT; PSTN_IN; PSTN_OUT; KIOSK; TEXT
class SessionState(StrEnum):
    CREATED; CONNECTING; LIVE; ENDING; PROCESSING; READY; REVIEWED; FAILED
class ConsentState(StrEnum): UNKNOWN; DISCLOSED; GRANTED; DECLINED

class Session(BaseModel):
    id: UUID; tenant_id: UUID; persona_id: str; persona_version: int
    mode: SessionMode; channel: Channel; state: SessionState
    consent_state: ConsentState; locale_hint: str | None
    started_at: datetime; ended_at: datetime | None
    outcome: str | None; cost_paise: int = 0
    def transition(self, to: SessionState) -> None: ...   # raises InvalidTransition
```

Event types as a tagged union: `SessionCreated`, `ConsentUpdated`, `AudioChunkReceived`, `TranscriptPartial`, `TranscriptFinal`, `AgentTurnDecided`, `AgentSpoke`, `ToolCalled`, `ToolCompleted`, `EscalationTriggered`, `HumanEdited`, `SessionEnded`. Every event: `session_id`, `seq`, `type`, `ts`, `payload`.

Protocols (`typing.Protocol`, async): `ASRProvider`, `LLMProvider`, `TTSProvider`, `EmbeddingProvider`, `EventBus`, `IngressAdapter`, `EgressAdapter`, `ToolExecutor`, `ObjectStore`.

**Accept:** state machine rejects illegal transitions (e.g. `CREATED → READY`) with a typed error; property test over all state pairs asserts only the legal set is accepted. `mypy --strict app/core` clean. `grep -r "^from app\." app/core/` returns only `app.core` imports.

---

#### T03 — Persona spec & validator ⊣ T02
**Files:** `app/core/persona.py`, `docs/contracts/persona.schema.json`, `personas/examples/*.yaml`
**Do:** Implement the Persona model (§3 below) with a `validate_for_publish()` that enforces: mode/channel compatibility, every tool resolvable, `identity.disclosure` present when `mode != OBSERVE`, retention within tenant policy, extraction schema is valid JSON Schema, at least one goal. Ship three example personas: `hospital_reception` (RESPOND/KIOSK), `loan_followup` (DRIVE/PSTN_OUT), `personal_recorder` (OBSERVE/MOBILE_MIC).
**Accept:** all three examples validate; a persona with `mode: RESPOND` and no disclosure fails with a specific error naming the field; publishing twice with the same version is rejected.

---

#### T04 — Database schema & repositories ⊣ T02
**Files:** `migrations/`, `app/infra/db.py`, `app/services/repositories/*.py`
**Do:** Alembic migrations for: `tenants`, `personas`, `sessions`, `session_events` (partitioned by month on `ts`), `turns`, `records`, `narratives`, `action_calls`, `media_assets`, `subjects`, `session_participants`, `embeddings` (pgvector), `quality_scores`. Enable RLS on every tenant-scoped table with a policy on `current_setting('app.tenant_id')`. Async repositories with a `tenant_scope()` context manager that sets the GUC.
**Accept:** integration test (testcontainers) proves tenant A cannot read tenant B's session **even with a raw SQL query that omits the WHERE clause**. `session_events` has no UPDATE/DELETE grant for the app role — test asserts both raise.

---

#### T05 — Event log & projections ⊣ T04
**Files:** `app/services/event_log.py`, `app/services/projections.py`
**Do:** `append(event)` with monotonic per-session `seq` (enforced by a unique constraint + retry on conflict, not a Python lock). `rebuild_projections(session_id)` reconstructs `turns`, `records`, `narratives` from events alone.
**Accept:** golden test — seed 200 events, snapshot projections, `TRUNCATE turns records narratives`, rebuild, assert byte-identical. Concurrent appends from 10 tasks produce a gapless `seq`.

---

#### T06 — Inference layer + fallback chain ⊣ T02
**Files:** `app/inference/{asr,llm,tts,embed}/`, `app/inference/chain.py`, `app/inference/budget.py`
**Do:** Provider adapters behind the T02 protocols. `FallbackChain` wraps N providers: try in order, circuit-break on repeated failure, record which provider served each call. `Budget` tracks per-session ASR seconds, LLM tokens in/out, TTS chars, telephony minutes → `sessions.cost_paise`. Model tiering config:

| Job | Tier | Constraint |
|---|---|---|
| Live dialogue turn | `fast` | streaming, first token < 350 ms |
| Structured extraction | `accurate` | schema-constrained decoding required |
| Final narrative | `accurate` | async, quality over latency |
| Intent routing | `classifier` | embedding match first, LLM only on low confidence |

Include a `FakeProvider` for every protocol — deterministic, used by all tests below.
**Accept:** chain falls through on a simulated 500 and records `provider_used`; circuit breaker opens after N failures and half-opens after cooldown; budget totals appear on the session row. No test calls a real paid API.

---

#### T07 — Schema-constrained extraction ⊣ T06, T03
**Files:** `app/services/intelligence/extractor.py`
**Do:** Given a persona schema + transcript turns, produce a `Record` using constrained decoding (provider structured-output mode where available; self-hosted grammar-constrained decoder otherwise — behind one interface). **Every field must carry `source_turn_id`**; fields the model cannot ground are dropped and logged as `ungrounded_field`.
**Accept:** with a fake LLM that emits an out-of-schema field name, the extractor raises rather than storing it. With a hallucinated value not present in any turn, the field is dropped and counted. Grounding check runs *before* any judge call.

---

#### T08 — Narrative generator ⊣ T06
**Files:** `app/services/intelligence/narrator.py`
**Do:** Two entry points. `incremental(session_id, since_seq)` — cheap, runs every N turns during a session, produces a preview. `final(session_id)` — regenerates from full context after the session ends, plus `action_items[]`. The final one does **not** extend the incremental one.
**Accept:** final narrative on a 60-turn fixture mentions every required persona field that was filled; incremental output is marked `is_preview=true` and never written to `narratives` as `final`.

---

#### T09 — TEXT adapter, end to end ⊣ T05, T07, T08
**Files:** `app/ingress/text.py`, `app/api/v1/sessions.py`, `app/services/session_service.py`
**Do:** Full lifecycle over keyboard input only. `POST /v1/sessions` → `POST /v1/sessions/{id}/messages` → `POST /v1/sessions/{id}/end` → record + narrative. Wire `session_service` to persona resolution, event log, projections.
**Accept:** **PHASE 0 GATE.** One integration test drives a 10-turn `hospital_reception` conversation via HTTP and asserts a populated `Record` and a `Narrative`. This test is the regression suite for everything after — it must never be deleted or weakened.

---

### Phase 1 — Passive audio (Surface A ships)

---

#### T10 — Chunked upload & media assets ⊣ T04
**Files:** `app/api/v1/media.py`, `app/infra/s3.py`, `app/services/media_assembly.py`
**Do:** Resumable chunked upload keyed on client-supplied `chunk_seq`. Reassemble by sequence, not arrival order; tolerate gaps (record them as `[GAP: n ms]` markers — iOS will kill long recordings). SHA-256 per chunk. Per-tenant KMS key reference on the asset. `POST /finalize` triggers the async pipeline.
**Accept:** out-of-order upload of 50 chunks reassembles correctly; a missing chunk yields a gap marker, not a failure; duplicate `chunk_seq` is idempotent.

---

#### T11 — Async pipeline & workers ⊣ T10, T07, T08
**Files:** `app/workers/`, `app/infra/bus.py`
**Do:** `EventBus` over Redis Streams with consumer groups. Pipeline on `session.ended`: assemble → diarise → reconcile transcript → extract → narrate → embed → score → webhook. **Each step idempotent and independently resumable**; a crash mid-pipeline resumes from the last completed step.
**Accept:** kill the worker after `extract` and restart — the pipeline resumes at `narrate` and does not re-run extraction. Poison message goes to a DLQ after N attempts without blocking the stream.

---

#### T12 — Diarisation & transcript reconciliation ⊣ T11
**Files:** `app/services/intelligence/diarize.py`, `.../reconcile.py`
**Do:** Offline diarisation on the assembled asset. Reconciliation rule: **live ASR wins on text, offline diarisation wins on speaker attribution.** Where the channel provides per-participant streams (meeting bots), skip diarisation entirely and use them.
**Accept:** on a 2-speaker fixture, DER below the threshold in `tests/eval/thresholds.yaml`; per-participant path bypasses the diariser (asserted by a spy).

---

#### T13 — Review & edit API ⊣ T05
**Files:** `app/api/v1/review.py`
**Do:** `PATCH /records/{id}` field-level edits, `PATCH /turns/{id}` transcript correction, `POST /sessions/{id}/approve`. **Human edits never overwrite the AI original** — both persist, the edit is a `HumanEdited` event.
**Accept:** after an edit, the original value is recoverable from the event log and `edited_by`/`edited_at` are set; approving locks further edits without an explicit reopen.

---

#### T14 — Search & analytics ⊣ T11
**Files:** `app/api/v1/search.py`, `app/api/v1/analytics.py`
**Do:** Hybrid search — Postgres FTS + pgvector cosine, fused. Filters: date, persona, outcome, subject, language. Analytics off a read replica connection, never the primary.
**Accept:** semantic query returns a session whose narrative shares no keywords with the query; analytics endpoint uses the replica DSN (asserted).

---

#### T15 — Consent, retention, erasure ⊣ T04, T10
**Files:** `app/services/consent.py`, `app/workers/retention.py`, `app/api/v1/subjects.py`
**Do:** Consent state machine with a working **DECLINED** path — transcribe-and-discard mode where no audio is persisted. Retention worker drops expired media and event partitions per tenant policy. `DELETE /v1/subjects/{id}/data` cascades across media, turns, records, embeddings and archives.
**Accept:** **PHASE 1 GATE.** With consent declined, zero bytes reach object storage (asserted at the S3 client). Erasure test creates a subject with 3 sessions, deletes, and a full-text scan of every table plus the bucket finds no trace. This test is a compliance artifact — treat it as such.

---

### Phase 2 — Real-time loop (kiosk first)

Kiosk before telephony: controlled acoustics, controlled network, no carrier variables.

---

#### T16 — Media plane: framing, VAD, endpointing ⊣ T02
**Files:** `app/media/frames.py`, `app/media/vad.py`, `app/media/endpoint.py`, `app/media/resample.py`
**Do:** Normalise any input to PCM16/16k/mono/20 ms frames. VAD state machine: `SILENCE → SPEECH → TRAILING → ENDPOINT`. Trailing-silence threshold is **per-persona** (~500–700 ms transactional, ~900–1200 ms healthcare). Semantic guard: extend the window if the partial transcript ends mid-clause or on a filler (`um`, `matlab`, `one second`). Jitter buffer. Resampler that refuses to upsample unless explicitly told a downstream model requires it.
**Accept:** on labelled fixtures, endpoint decisions land within tolerance of ground truth; a fixture with a mid-sentence 800 ms pause does **not** trigger an endpoint at the 700 ms threshold.

---

#### T17 — media_gateway service ⊣ T16, T11
**Files:** `app/services/media_gateway/`
**Do:** Owns one session's media for its lifetime. WebSocket termination, sticky by `session_id`. Streaming ASR partials + finals onto the bus. **Never awaits an LLM or TTS call.** Graceful drain: stop accepting new sessions, let live ones finish, then recycle.
**Accept:** a simulated 30 s LLM hang does not drop the audio socket or lose frames; drain signal completes without killing a live session.

---

#### T18 — agent_runtime ⊣ T17, T03
**Files:** `app/services/agent_runtime/`
**Do:** Goal-directed slot filler with LLM surface language:

```python
async def decide(ctx: TurnContext) -> TurnDecision:
    """ctx: history, filled_slots, missing_slots, tools, sentiment, turn_count
       returns: utterance | tool_intents | state_delta | escalate | close"""
```
Guardrails **enforced in code, not in the prompt**: turn cap, duration cap, repeated-question detector (escalate on 2 repeats), sentiment threshold, out-of-scope → handoff. Speculative generation on stable partials behind a per-persona flag, cancellable.
**Accept:** repeated-question fixture escalates rather than looping; turn cap triggers a graceful close, not a hang; speculative generation is cancelled when the user resumes speaking, with no orphaned LLM call.

---

#### T19 — TTS egress & barge-in ⊣ T17
**Files:** `app/media/egress.py`, `app/inference/tts/streaming.py`
**Do:** Sentence-chunked streaming TTS — start emitting audio before the utterance completes. Barge-in: on VAD speech during agent playback, stop TTS, flush the outbound buffer, send the channel's clear signal, discard the interrupted turn. Pre-synthesised backchannel cache ("mm-hmm", "let me check") emitted at ~800 ms when the budget is at risk.
**Accept:** barge-in stops audio within 200 ms of detected speech and the interrupted turn is not persisted as `AgentSpoke`; backchannel fires only when the turn exceeds 800 ms.

---

#### T20 — Latency instrumentation ⊣ T19
**Files:** `app/infra/telemetry.py`
**Do:** Emit each stage **separately**: endpoint detect, ASR flush, routing, LLM first token, TTS first chunk, network. Targets: **≤ 900 ms p50, ≤ 1.5 s p95** end-of-speech → first audible response. OpenTelemetry traces correlated by `session_id`.
**Accept:** a load test of 20 concurrent sessions reports all six stage histograms; a synthetic 400 ms regression in TTS is attributable to that stage alone from the dashboard.

---

#### T21 — action_service ⊣ T18
**Files:** `app/services/action_service/`
**Do:** Tool registry per tenant. Idempotency key = `hash(session_id, tool, normalised_args)`, unique-constrained. Approval tiers `AUTO | CONFIRM_IN_CONVERSATION | HUMAN_REVIEW`. `CONFIRM_IN_CONVERSATION` reads the action back and requires an affirmative. Results injected back as a system turn. Full audit row per invocation. Transports: HTTP, MCP, internal.
**Accept:** double-submit with the same key executes once and returns the first result; an irreversible tool without confirmation is refused; tool args failing schema validation never reach the transport.

---

#### T22 — KIOSK adapter ⊣ T19, T21
**Files:** `app/ingress/kiosk.py`, `app/api/v1/kiosk.py`
**Do:** WebRTC mic, **keyboard fallback always available** (accessibility + noisy lobbies), camera for document/QR/OCR as discrete requests, not a stream. **No biometrics in v1.** Device-certificate identity + tenant location config.
**Accept:** **PHASE 2 GATE.** End-to-end kiosk session: greeting → slot filling → tool call → close, meeting the T20 latency budget on the reference hardware profile.

---

### Phase 3 — Telephony (Surface C)

---

#### T23 — Telephony provider abstraction ⊣ T17
**Files:** `app/ingress/telephony/{base,twilio,exotel}.py`
**Do:** One interface, two implementations from the start — assume Exotel for India and Twilio for international run simultaneously. Handle: call control document generation, media socket, signature validation, mulaw↔PCM conversion, `mark` events for playback completion. **Bidirectional media** (`<Connect><Stream>` semantics), not listen-only — the agent must speak.
**Accept:** provider-agnostic contract tests run against both adapters; unsigned webhook → 403 with no body logged; mulaw round-trip is lossless at the byte level.

---

#### T24 — Outbound campaigns ⊣ T23
**Files:** `app/services/outbound/`
**Do:** Campaign runner with **answering-machine detection** (without it the agent qualifies voicemail and burns tokens) and **number-pool rotation** — 5–10 numbers, hard cap 50–80 calls/day/number, because a single number past ~200–300 calls/day with short durations gets carrier spam-flagged within weeks. Retry/disposition ladder. Per-tenant concurrency cap.
**Accept:** the pool never exceeds the per-number daily cap under a 500-call simulation; AMD-positive calls terminate without an agent turn; concurrency cap queues rather than drops.

---

#### T25 — Warm transfer & escalation ⊣ T24
**Files:** `app/services/handoff.py`
**Do:** PSTN warm transfer, queue-with-context for chat/kiosk. The human receives live transcript + filled slots. Escalation is a first-class **outcome**, not a failure path.
**Accept:** transfer preserves `session_id` continuity and the receiving agent's payload contains the filled slots at the moment of transfer.

---

### Phase 4 — Meetings

---

#### T26 — Meeting capture provider ⊣ T11
**Files:** `app/ingress/meeting.py`
**Do:** `MeetingCaptureProvider` interface, vendor-backed initially (managed bot API). Do **not** operate headless-browser fleets in v1. Prefer per-participant audio streams where offered — they make diarisation nearly free. Handle: join, participant events, live audio over WS, post-meeting recording fallback.
**Accept:** interface has zero vendor types in its signature; a second stub provider can be swapped by config alone.

---

#### T27 — Calendar-triggered join ⊣ T26
**Do:** Watch tenant calendars, dispatch bots, handle host-permission failures gracefully (the Meet Media API path rejects on encryption, watermarks, underage participants, missing admin/host approval, and can be revoked mid-call — surface these as typed, user-legible errors, never as a generic failure).
**Accept:** each rejection reason maps to a distinct typed error and a distinct user-facing message.

---

### Phase 5 — Self-service

T28 persona builder API · T29 tool registry UI backend · T30 tenant webhooks (HMAC-signed, retried, replayable) · T31 quality scoring + judge calibration against 5% human review · T32 golden eval harness (50+ labelled recordings per domain/language, run on every model or prompt change).

---

## 2. Latency budget (T20 targets)

| Stage | p50 | Owner |
|---|---|---|
| Endpoint detection | 250 ms | `app/media/endpoint.py` |
| Final ASR flush | 150 ms | `app/inference/asr` |
| Agent routing + state | 20 ms | `agent_runtime` (no DB read on the hot path) |
| LLM first token | 350 ms | `fast` tier |
| TTS first chunk | 200 ms | streaming, sentence-chunked |
| Network + jitter | 80 ms | `media_gateway` |

---

## 3. Persona spec (implemented in T03)

```yaml
persona:
  id: hospital_reception
  version: 1
  tenant_id: <uuid>
  mode: RESPOND
  channels: [KIOSK, PSTN_IN]

  language:
    primary: ta-IN
    accepted: [ta-IN, en-IN, hi-IN]
    code_mixed: true
    respond_in: MIRROR_USER        # MIRROR_USER | FIXED
    script_policy: NATIVE          # NATIVE | ROMANISED

  voice: {provider_voice_id, speaking_rate, gender}

  identity:
    role_description: str
    opening_utterance: str
    disclosure: str                # REQUIRED when mode != OBSERVE
    guardrails: [str]              # injected AND enforced in code

  turn_taking:
    trailing_silence_ms: 900
    speculative_generation: false
    backchannel_after_ms: 800

  goals:
    - id: identify_patient
      required_slots: [name, phone, dob_or_id]
    - id: book_or_route
      required_slots: [department, preferred_slot]

  schema:                          # extraction target — valid JSON Schema
    fields: [{name, type, description, required, pii}]

  tools:
    - name: book_appointment
      input_schema: {...}
      approval: CONFIRM_IN_CONVERSATION
      idempotency: required
      timeout_ms: 3000
      on_failure: ESCALATE

  escalation:
    max_turns: 20
    max_duration_ms: 600000
    on_sentiment_below: -0.6
    on_repeat_count: 2
    target: {type: PSTN_TRANSFER, number_ref: front_desk}

  retention:
    audio_days: 30
    transcript_days: 365
    pii_masking: ON_STORE
```

---

## 4. Open decisions

Do not silently resolve these. Implement behind the protocol, choose the simplest option, log the choice in `docs/decisions.md`.

| # | Question | Blocks | Default until decided |
|---|---|---|---|
| O1 | Bus: Redis Streams vs NATS JetStream | T11 | Redis Streams |
| O2 | Meeting capture vendor | T26 | Interface + stub |
| O3 | Primary ASR per language tier — **benchmark on real 8 kHz telephony audio, not clean 16 kHz samples** | T06, T23 | Fallback chain, provider TBD |
| O4 | Dialogue LLM: hosted vs self-hosted (latency, cost, residency) | T18 | Hosted `fast` tier |
| O5 | Telephony commercial terms (India + international) | T24 | Both adapters built |
| O6 | ABDM / FHIR profile scope | Phase 5 | Do not claim compliance |
| O7 | Per-tenant concurrency caps / noisy-neighbour policy | T24 | Global cap |

---

## 5. Definition of done (every task)

- [ ] `make verify` green (ruff + mypy + pytest)
- [ ] Tests in the same commit; integration tests use testcontainers, not mocks, for Postgres/Redis
- [ ] No invariant in `CLAUDE.md` violated
- [ ] New env vars documented in `.env.example`
- [ ] Alembic migration if the schema changed
- [ ] T09 phase-0 gate test still passes
- [ ] Any OPEN decision touched is recorded in `docs/decisions.md`
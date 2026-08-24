# Mobile App — Screen Specification

**Platform:** Flutter (iOS + Android)
**Audience:** Product designer and Flutter developer
**Scope:** Surface A — the personal recorder. Client-facing kiosk and agent surfaces are a separate Flutter target that shares the design system and API packages; they are not specified here.
**Companion docs:** `docs/MASTER_PLAN.md` (backend task graph), `CLAUDE.md` (backend invariants)

---

## 1. What this app is

A one-tap recorder that turns conversations and meetings into a **summary you can trust and correct**.

The product is not the recording. The recording is table stakes — every phone has one. The product is the moment after: a summary, the facts pulled out of it, and the ability to see exactly where each fact came from. Design decisions should be judged against that.

**The core loop:**
```
Record  →  (upload, process)  →  Read summary  →  Correct anything wrong  →  Find it again later
```

Everything in v1 serves that loop. If a screen doesn't, it's Phase 2.

---

## 2. Scope boundaries — read before designing

These constraints are platform-imposed and not negotiable by design. Designing around them later is expensive.

| Constraint | Design consequence |
|---|---|
| **The app cannot record phone calls.** Android has blocked third-party call recording since Android 10; iOS never permitted it. | No "record my call" affordance anywhere. Recording covers in-person conversations and meetings only. Onboarding must set this expectation, or the first support ticket is "why didn't it record my call?" |
| **iOS may kill a long background recording** under memory pressure, despite background audio mode. | Recording must be gap-tolerant and the UI must never claim a guarantee it can't keep. Show what was captured, not what was intended. |
| **Android requires a persistent foreground-service notification** while recording. | The notification is part of the design surface. It needs elapsed time, a stop control, and the app's identity. Design it. |
| **Recording another person carries legal and social weight**, and varies by state and context. | Consent is a designed flow, not a checkbox in settings. See §7. |
| **Meeting platforms do not hand out live audio.** Capture happens via a bot that visibly joins the meeting as a participant. | The bot appears in the participant list with a name other attendees will see. That name and its visibility are a design decision, not an implementation detail. |
| Processing a 60-minute recording takes minutes, not seconds. | Never block on processing. Notify. See §6.3. |

---

## 3. Information architecture

```
┌─ Onboarding (first run only)
│   S01 Welcome
│   S02 Sign in (phone + OTP)
│   S03 Language & region
│   S04 Permissions primer
│
└─ App shell (bottom nav, 3 tabs + persistent record button)
    │
    ├─ Tab 1 — Library          S10 Recordings list
    │                            S11 Search
    │                            S20 Session detail ──┬─ Summary tab
    │                                                 ├─ Transcript tab
    │                                                 └─ Highlights tab
    │                            S21 Edit summary
    │                            S22 Correct transcript
    │                            S23 Speaker labels
    │                            S24 Share & export
    │
    ├─ Tab 2 — Meetings         S30 Upcoming meetings
    │                            S31 Connect calendar
    │                            S32 Meeting capture settings
    │
    ├─ Tab 3 — Settings         S40 Account
    │                            S41 Recording defaults
    │                            S42 Language
    │                            S43 Privacy & retention
    │                            S44 Storage & uploads
    │
    └─ Record (modal, from FAB) S50 Pre-record consent
                                 S51 Recording
                                 S52 Live view (optional mode)
                                 S53 Post-record
```

**Navigation principle:** the record button is reachable from every tab in one tap and is never more than one tap from stop. Someone starting a recording is usually mid-conversation and not looking at the screen.

---

## 4. Screen specifications

Each screen lists: **purpose · states · content · interactions · edge cases**. States are mandatory — a screen without a designed empty, loading, error and offline state is not done.

---

### S01 — Welcome
**Purpose:** Explain the product in one screen and set the call-recording expectation immediately.
**Content:** Three-panel horizontal carousel: (1) record any conversation, (2) get a summary with sources, (3) find anything you've ever discussed. One primary CTA "Get started", one text link "Sign in".
**Must include:** a plain-language line stating the app records in-person conversations and online meetings, not phone calls. Put it here, not in the FAQ.
**States:** default only.

---

### S02 — Sign in
**Purpose:** Phone-number authentication with OTP.
**States:** `entry` · `otp_sent` (with resend countdown) · `verifying` · `error_invalid_otp` · `error_rate_limited` · `error_network`
**Content:** Country selector defaulting to +91, number field, OTP field with auto-read on Android, resend timer, support link.
**Edge cases:** OTP arrives after the user has retyped it (accept both); SIM-less tablet (offer email fallback or block gracefully); rate-limited resend must state when they can retry, not just refuse.

---

### S03 — Language & region
**Purpose:** Set primary language and accepted languages for transcription.
**Content:** Primary language selector. Multi-select for "languages you might switch between" — default to primary + English. A short explanation that mixing languages mid-sentence is expected and supported.
**Why this screen exists:** users in India routinely mix Tamil/Hindi/English within a sentence. Asking here produces better transcription and signals that the product understands their speech. It's also a differentiation moment — don't bury it in settings.
**States:** default · saving · error.

---

### S04 — Permissions primer
**Purpose:** Explain *before* the OS dialog appears why each permission is needed. Never fire a system permission dialog cold.
**Content:** One row per permission — microphone (required), notifications (recommended — recording status and summary-ready alerts), calendar (optional, for meetings). Each row: what it's for, one sentence, and a toggle that triggers the OS prompt.
**States:** `not_requested` · `granted` · `denied` · `permanently_denied` (must deep-link to OS settings with instructions).
**Edge case:** mic permanently denied is a dead-end app. Design that screen explicitly — do not let the user reach the record button and discover it there.

---

### S10 — Recordings list *(Tab 1, home)*
**Purpose:** The default screen. Everything the user has recorded, most recent first.

**States:**
- `empty` — first run. Illustration + "Record your first conversation" + the FAB pulsing once.
- `loading` — skeleton rows, not a spinner.
- `loaded` — list.
- `error` — cached list plus a retry banner. Never a blank screen; local recordings exist regardless of network.
- `offline` — full list from local cache, with an offline chip in the header.

**Row anatomy:**
```
[status dot] Title (auto-generated or user-set)
             Date · Duration · Language chips
             ── one-line summary preview ──
             [progress bar if uploading/processing]
```

**Row status states — this is the most important detail on the screen:**

| Status | Meaning | Visual |
|---|---|---|
| `recording` | Currently in progress | Live pulse, elapsed time counting |
| `saved_local` | On device, not yet uploaded | Solid dot, "Saved on this device" |
| `uploading` | Upload in progress | Determinate progress bar with % |
| `queued` | Waiting for connectivity or Wi-Fi | Muted dot, "Waiting for Wi-Fi" |
| `processing` | Backend is transcribing/summarising | Indeterminate shimmer, "Preparing summary" |
| `ready` | Summary available | Normal, summary preview shown |
| `failed` | Processing failed | Warning colour, tappable to retry |
| `no_recording` | Consent declined — transcript only, no audio kept | Distinct icon, explained on tap |

**Why so many:** the single largest source of anxiety in a recorder app is "did it save?". Every state above must be legible at a glance, without tapping.

**Interactions:** tap → S20. Long-press → context menu (rename, share, delete). Pull to refresh. Swipe to delete with undo (destructive, always undoable for 5 seconds).
**Grouping:** Today / Yesterday / This week / month headers.

---

### S11 — Search
**Purpose:** Find a past conversation by what was said, not just by title.
**Content:** Search field, recent searches, filter chips (date range, language, speaker, has-action-items).
**States:** `idle` (recent + suggestions) · `typing` (debounced) · `results` · `no_results` (with a suggestion to broaden) · `error`.
**Result row:** title, date, and the **matched snippet with the query term highlighted** — not just the title. Semantic matches won't contain the literal query term; in that case show the most relevant sentence and mark it as a related match so the user isn't confused by the absence of a highlight.

---

### S20 — Session detail
**Purpose:** The payoff screen. Three tabs over a persistent audio player.

**Layout:**
```
┌──────────────────────────────┐
│ ← Title                  ⋯   │
│ Date · 42:15 · Tamil/English │
├──────────────────────────────┤
│  Summary │ Transcript │ Notes│   ← tabs
├──────────────────────────────┤
│                              │
│         tab content          │
│                              │
├──────────────────────────────┤
│ ▶ ──────●───────── 12:04     │   ← persistent mini player
└──────────────────────────────┘
```

**Tab 1 — Summary**
- Narrative paragraph(s)
- **Key facts** — the structured record, rendered as label/value rows
- **Action items** — checkbox list
- **Every fact and every summary sentence is tappable and jumps the player + transcript to its source moment.** This is the trust mechanism of the entire product. A summary you can't verify is a summary you won't rely on. Show the link affordance subtly but always (a small timestamp chip, not a full link treatment).
- Low-confidence fields get a distinct visual weight and a "check this" affordance. Do not hide uncertainty.
- Empty state: if extraction found nothing (a casual chat, not a structured conversation), say so plainly rather than showing empty field rows.

**Tab 2 — Transcript**
- Speaker-grouped blocks: avatar/colour, speaker name or `Speaker 1`, timestamp, text
- Language tag on code-mixed segments
- Low-confidence segments visually flagged and tappable to correct
- Auto-scroll follows playback; scrolling manually detaches it, with a "jump to current" pill to reattach
- Gap markers (`recording interrupted, 8s`) rendered honestly inline
- Search-within-transcript

**Tab 3 — Notes**
- User's own typed notes, timestamped against the recording
- Notes taken during recording appear here anchored to their moment

**Player:** speed control (1x/1.25x/1.5x/2x), 15s skip, scrubber with waveform, background playback.

**Edge case:** consent-declined sessions have transcript and summary but **no audio**. The player must be absent, not disabled-and-mysterious, with a one-line explanation.

---

### S21 — Edit summary
**Purpose:** Correct a field or rewrite a summary line.
**Behaviour:** Inline field editing with the original AI value shown as struck-through or in a "was" affordance. **Human edits never destroy the AI original** — the backend keeps both, so the UI can offer "revert to original".
**States:** `viewing` · `editing` · `saving` · `saved` (brief confirmation) · `conflict` (edited elsewhere — offer both versions) · `error`.

---

### S22 — Correct transcript
**Purpose:** Fix a mis-transcribed segment.
**Content:** The segment in a text field, the audio for just that segment on a loop-play button, original text recoverable.
**Interaction:** correcting a segment that a summary fact was derived from should prompt: "This was used in your summary. Update it?"

---

### S23 — Speaker labels
**Purpose:** Turn `Speaker 1` into `Dr. Menon`.
**Content:** One row per detected speaker with a colour swatch, a sample utterance with a play button, and a name field. Optional "remember this voice" — **off by default, with a clear explanation**, since a stored voiceprint is sensitive data.
**Edge case:** the diariser may over-split (one person as two speakers) or under-split. Offer merge and split. Set expectations: far-field in-person recording is the hardest case and will need correction more often than a meeting.

---

### S24 — Share & export
**Purpose:** Get the summary out of the app.
**Options:** copy summary, share as text, export PDF, export transcript (.txt/.srt), share audio (with a consent warning), send to email.
**Design note:** sharing audio of a third party is the highest-risk action in the app. It gets a confirmation dialog that names the risk, not a generic "Are you sure?".

---

### S30 — Upcoming meetings *(Tab 2)*
**Purpose:** Choose which meetings to capture.
**States:** `not_connected` (connect-calendar CTA + value explanation) · `connected_empty` · `loaded` · `error`.
**Row:** meeting title, time, platform icon, participant count, and a **capture toggle**.
**Critical disclosure:** the row must state that an assistant will **join the meeting as a visible participant**. Attendees will see it. Burying this is a trust failure that surfaces in the worst possible moment — mid-meeting, in front of the user's colleagues.
**States per meeting:** `will_join` · `joining` · `in_progress` · `completed` · `failed_to_join` (with a specific reason — see below) · `skipped`.

---

### S31 — Connect calendar
**Purpose:** OAuth flow for calendar access.
**States:** `intro` · `authorising` (external browser) · `success` · `error_denied` · `error_scope_insufficient`.
**Design note:** explain scope in plain language before the OAuth screen. Users abandon at the Google consent screen when they haven't been told why.

---

### S32 — Meeting capture settings
**Content:** Bot display name (user-editable, defaults to `<User>'s Notetaker`), auto-join rules (all meetings / only meetings I organise / only ones I toggle), join announcement on/off.
**Failure messaging — do not use a generic error.** Meeting capture fails for specific, user-actionable reasons: the host hasn't approved the app, the meeting is encrypted or watermarked, an admin setting blocks it, an underage participant is present, or the host revoked access mid-call. Each needs its own message and, where possible, its own remedy. "Couldn't join the meeting" teaches the user the feature is unreliable; "The meeting host needs to approve notetakers in their Calendar settings" teaches them how to fix it.

---

### S40–S44 — Settings
- **S40 Account** — profile, plan, sign out, delete account (must actually erase; see S43)
- **S41 Recording defaults** — quality, live mode on/off, auto-upload on Wi-Fi only, default title format
- **S42 Language** — primary + accepted languages, app UI language (independent of transcription language)
- **S43 Privacy & retention** — how long audio is kept (default 30 days) and transcripts (default 365), consent defaults, **"Delete all my data"** with a real confirmation and an honest statement of what is and isn't recoverable
- **S44 Storage & uploads** — local storage used, pending upload queue with per-item retry, "upload now over mobile data" override

---

### S50 — Pre-record consent
**Purpose:** The screen between tapping record and recording starting.

**This screen is the product's ethical posture and it must be fast.** Someone is standing in front of another person waiting. Target: under two seconds and one tap.

**Content:** Language selector (pre-filled from S03, one tap to change), optional title, and a consent action. Two configurable modes in S41:
- **Announce** — plays an audible disclosure ("This conversation is being recorded") before recording starts
- **Silent** — no announcement; the user takes responsibility, stated plainly once

**Primary CTA:** "Start recording". Secondary: cancel.
**Repeat-use behaviour:** after the first few sessions, offer "don't ask again" which reduces this to a single confirmation toast — but never removes it entirely.

---

### S51 — Recording *(the hero screen)*
**Purpose:** Reassure, continuously, that recording is working.

**Content, in priority order:**
1. **Elapsed time**, large. The single most reassuring element.
2. **Live waveform or level meter** driven by actual mic input — a fake animation is worse than none, because a user watching it move during silence learns not to trust it.
3. Status line: "Recording · Saved on this device"
4. **Pause** and **Stop** — Stop requires a deliberate action (hold, or a confirm) so a pocket tap doesn't end a meeting
5. **Add note** — timestamped marker, opens a small text field without interrupting recording
6. **Flag moment** — one tap, drops a marker for later review

**States:** `recording` · `paused` · `interrupted` (incoming call took the mic — this must be visible and explained, and recording must auto-resume after) · `low_storage_warning` · `stopping`.

**Background:** must keep running when the app is backgrounded or the screen is locked. Android foreground-service notification carries elapsed time and a stop action. iOS lock-screen media controls likewise. **Design both — they are screens.**

**Anti-requirement:** no animation that continues when recording has silently stopped. If capture dies, the UI must go loud, not calm.

---

### S52 — Live view *(optional mode, off by default)*
**Purpose:** Real-time transcript and building summary for users who want it.
**Content:** Live transcript feed with partial results in a lighter weight, finalising to full weight; a summary panel that updates every few turns, clearly marked as **a preview that will be regenerated**.
**Why default off:** live mode costs battery and network and adds failure modes. Most users want the summary afterwards. Make it a deliberate opt-in.
**States:** `connecting` · `live` · `degraded` (transcript lagging or dropped — recording continues, and say so) · `reconnecting`.
**Critical:** if the live transcript connection dies, **recording must continue locally** and the UI must say exactly that. Losing the transcript is an inconvenience; losing the recording is a catastrophe, and the user must be able to tell which one happened.

---

### S53 — Post-record
**Purpose:** The handoff between stopping and the summary being ready.
**Content:** Duration, confirmation it's saved locally, upload state, editable title, "Processing your summary — we'll notify you" with an estimate.
**Do not block.** The user returns to S10 immediately; the row shows progress there.
**States:** `saved` · `uploading` · `queued_offline` · `processing` · `ready` (deep-link straight to S20) · `failed` (retry).

---

## 5. Cross-cutting state machines

The designer needs these as much as the developer, because each transition is a UI moment.

**Recording**
```
IDLE → CONSENT → RECORDING ⇄ PAUSED → STOPPING → SAVED_LOCAL
                     ↓
                INTERRUPTED (call / OS) → auto-resume → RECORDING
                     ↓
                 FAILED (mic lost, storage full) → PARTIAL_SAVED
```

**Upload**
```
SAVED_LOCAL → QUEUED → UPLOADING ⇄ PAUSED(no network) → UPLOADED
                            ↓
                        FAILED → retry with backoff → QUEUED
```

**Processing**
```
UPLOADED → PROCESSING → READY
                ↓
             FAILED → retryable? → QUEUED : NEEDS_SUPPORT
```

Every terminal failure state needs designed copy that says what happened, what was preserved, and what the user can do.

---

## 6. Global patterns

**6.1 Empty states** — every list gets one, with a single clear action. Never an empty rectangle.

**6.2 Offline** — the app is fully functional offline for recording and reading anything already downloaded. A persistent, unobtrusive offline indicator in the header; a queued-uploads count in Tab 1. Offline must never feel like breakage, because a user recording in a hospital basement is the target user, not an edge case.

**6.3 Notifications** — recording in progress (persistent, Android), summary ready (tappable, deep-links to S20), upload failed after retries, meeting bot joined/failed. Nothing else. Notification fatigue kills the summary-ready notification, which is the one that matters.

**6.4 Errors** — never a raw error code. Every error states what happened, what was preserved, and one action. Distinguish *your recording is safe but X failed* from *X failed and data was lost* — visually and in wording.

**6.5 Destructive actions** — undo over confirm wherever possible (5-second undo snackbar). Confirm dialogs only for genuinely irreversible actions: delete-all, share third-party audio, account deletion.

---

## 7. Consent and privacy as design surface

Recording another person is the app's central ethical and legal exposure. Design decisions:

- Consent is a **flow** (S50), not a settings toggle
- An audible announcement option exists and is easy to reach
- The meeting bot is **visibly named** in the participant list — the user chooses the name
- Retention is user-visible and user-controllable (S43)
- "Delete all my data" genuinely deletes, and the copy says exactly what that covers
- If consent is declined, the session runs in transcript-only mode with no audio stored — and the UI shows this clearly rather than silently behaving differently

Treat this section as a feature. For hospital and financial users it is the reason they can install the app at all.

---

## 8. Design system foundations

Enough for the designer to start; expand into a full Figma library.

**Type:** one family, five roles — Display (elapsed time, 48–64), Title (20), Body (16), Caption (13), Mono (timestamps, 13). Must render Tamil, Devanagari and Latin without fallback shifts — **test the type ramp in all three scripts before committing to a family**. Indic scripts have taller line boxes; a leading value that looks right in Latin will clip.

**Colour roles** (not values — the designer picks the palette):
`surface` · `surface-elevated` · `content-primary` · `content-secondary` · `accent` (record/primary action) · `positive` (ready, saved) · `attention` (low confidence, needs review) · `critical` (failure, destructive) · `muted` (queued, offline)

Recording state deserves a colour used nowhere else in the app.

**Spacing:** 4pt base, steps 4/8/12/16/24/32/48.

**Motion:** fast and functional. 150–200ms for state changes, 250–300ms for transitions. The only expressive motion is the waveform, and it is **data-driven, never decorative**.

**Touch targets:** 48dp minimum. The stop button gets more.

**Dark mode:** required, not optional. Recordings happen in clinics, cars and evening meetings.

---

## 9. Accessibility

- Full screen-reader labels, especially on recording state — a blind user must be able to confirm recording is active
- Recording status must not be conveyed by colour alone (pair with the elapsed timer and an explicit text label)
- Dynamic type up to 200% without layout breakage; the recordings list and transcript are the hard cases
- Transcript text selectable and copyable
- Playback speed control benefits users with cognitive load, not just power users

---

## 10. Localisation

- **UI language is independent of transcription language.** A user may read the app in English while recording in Tamil. Do not couple them.
- v1 UI languages: English, Hindi, Tamil. Architecture ready for more.
- No concatenated strings — full sentences with placeholders, always. "Recording saved" and "3 recordings queued" are different grammatical shapes in Hindi and Tamil.
- Date, time and number formatting per locale.
- Expect 30–40% string expansion in Hindi versus English. Design with the longest string, not the English one.

---

## 11. API bindings

Screen → endpoint, so the developer can build against the backend contract in `docs/MASTER_PLAN.md`.

| Screen | Endpoints |
|---|---|
| S02 | `POST /v1/auth/otp`, `POST /v1/auth/verify` |
| S10 | `GET /v1/sessions?filters` |
| S11 | `POST /v1/search` |
| S20 | `GET /v1/sessions/:id`, `/transcript`, `/record`, `/narrative` |
| S21/S22 | `PATCH /v1/sessions/:id/record`, `PATCH /v1/turns/:id` |
| S23 | `PATCH /v1/sessions/:id/participants` |
| S30/S31 | `POST /v1/meetings/join`, calendar OAuth |
| S43 | `DELETE /v1/subjects/:id/data` |
| S50 | `POST /v1/sessions` (channel `MOBILE_MIC`, mode `OBSERVE`) |
| S51 | `POST /v1/sessions/:id/chunks` (resumable, `chunk_seq`) |
| S52 | `WS /v1/stream/:session_id` |
| S53 | `POST /v1/sessions/:id/finalize`, then `session.ready` webhook → push notification |

---

## 12. Open design questions

Decide these before high-fidelity design, not during.

1. **Is live mode (S52) in v1 at all?** It roughly doubles the mobile surface area and the failure modes. Recommendation: build the backend for it, ship the app without it, add it once deferred mode is solid.
2. **Bot display name default** for meeting capture — the user's name, the product name, or forced-custom? This is the first thing the user's colleagues will see.
3. **Free tier limits** — minutes/month, retention, or feature-gated? This shapes S10 and S40 substantially and is easier to design in than to retrofit.
4. **Does the recorder need multi-speaker naming in v1** (S23), or is `Speaker 1 / Speaker 2` acceptable for launch? Speaker labelling is high effort for a benefit most solo-note users don't need.
5. **Widget / quick-action recording** — lock-screen widget, Siri shortcut, Android quick-settings tile. High value for "record right now" but each is platform-specific work.
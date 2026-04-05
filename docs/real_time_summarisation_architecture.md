# VaakSetu: Conversational Voice AI Platform
**Architecture & Technical Pipeline Documentation**

VaakSetu is an enterprise-grade, ultra-low latency, multi-modal Voice AI platform engineered specifically for the intricate linguistic landscape of India. It fluidly handles real-time telephonic integration, real-time code-switching (e.g., Hinglish, Tanglish), domain-specific data extraction, and offline multi-speaker summarisation.

---

## 1. High-Level Architecture Overview

VaakSetu operates as a real-time event-streaming duplex pipeline bridging the physical telephone network/web UI to state-of-the-art Neural conversational models.

```mermaid
graph TD
    subgraph Client Acquisition Layer
        WebUI[Next.js Dashboard & Mic]
        PSTN[Cell Phone User]
    end

    subgraph Transport & Telephony Layer
        Browser[HTTPS / MediaRecorder API]
        Twilio[Twilio Voice Engine]
        Ngrok[Ngrok WSS Tunnel]
    end

    subgraph Backend Application (FastAPI)
        Route[REST & WebSocket Routers]
        AudioProc[PyDub/AudioOp UpSampler]
    end

    subgraph Deep Learning Engine
        ASR[Sarvam STT / IndicWhisper]
        LLM[SmartDialogueAgent / Sarvam-M]
        EXTRACT[SmartExtractor / LangChain]
        TTS[Sarvam TTS / Bulbul v2]
    end

    subgraph Ancillary AI Services
        DIAR[Pyannote Diarization]
        RWAIF[Prometheus Reward Engine]
    end
    
    WebUI <--> Browser
    PSTN <--> Twilio
    Twilio <--> Ngrok
    Ngrok <--> Route
    Browser <--> Route
    Route <--> AudioProc
    AudioProc --> ASR
    ASR --> LLM
    ASR --> EXTRACT
    LLM --> TTS
    TTS --> Route
```

---

## 2. Audio Acquisition & Processing

We accept audio from two radically different acoustic environments: pristine Web audio and compressed telecom audio. Both need normalization before hitting the AI layer.

### 2.1 Web UI (Next.js)
The frontend utilizes the `MediaRecorder` API allowing the user to press to talk. The browser typically records Opus encoded audio encapsulated in `WebM` blobs. These blobs are transmitted over standard HTTP boundaries to the backend.

### 2.2 Telephony (Twilio & Ngrok)
Live cell phone calls are integrated via Twilio Webhooks (`/api/calls/twiml`). When a PSTN connection is made, Twilio executes TwiML `<Start><Stream>` which forcefully negotiates an asymmetric WebSocket back to our local runtime over an `Ngrok WSS Tunnel`.

- **Topological Audio Engineering:** Telecom streams arrive internally heavily compressed as `audio/x-mulaw` bytes at 8,000Hz.
- Using Python's native `audioop` module, the backend decodes the stream into flat 16-bit PCM tracks, and aggressively up-samples the waveform to a full 16,000Hz (required for Deep Learning audio processors) synchronously as chunk bytes arrive.

---

## 3. The Core Artificial Intelligence Engine

Once standard 16kHz audio arrives, we initiate parallel LLM computation.

### 3.1 Speech-to-Text Pipeline (ASR)
- **Primary:** Cloud-based integration with **Sarvam AI (saaras:v3)** specifically fine-tuned for dense Indian dialects and background noise handling.
- **Fail-Over / Air-Gapped:** We enforce an automated resilience mechanism. If rate limits are exceeded, transcription seamlessly falls back to a locally executed Hugging Face endpoint running **AI4Bharat IndicWhisper**.

### 3.2 Dual-Parallel Generation (`SmartDialogueAgent`)
To drastically cut down time to first byte, when the text arrives, standard systems run extraction first, then dialogue secondly. **VaakSetu parallelizes execution using Python's `asyncio.gather`:**

#### A. Conversational Loop (`ChatOpenAI` / Sarvam-M)
The dialogue brain manages natural interaction. It continually reconstructs a highly contextual **System Prompt** dynamically loaded from our SQLite configuration database. The model is rigidly forced to be a "Live Person", adhering strictly to the user's current linguistic structure. **If the transcript is Tanglish, the LLM outputs perfect, grammatically correct Tanglish.**

#### B. The Structured Extraction Engine (`SmartExtractor`)
Whilst the model figures out how to talk back, our LangChain Node intercepts the transcript and maps user speech against Pydantic models (e.g., `HealthcareExtraction`, `FinanceExtraction`).
- **Healthcare:** Dynamically maps *Symptoms*, *Diagnosis*, *Treatment Plan*.
- **Finance:** Dynamically maps *Intent*, *Amount*, *Urgency*.
- It logs retrieved datapoints silently to `collected_fields` inside the agent's memory, feeding back only "Missing Fields" to the conversational loop, ensuring the bot natively drives the user towards filling out the remaining form.

### 3.3 Dynamic Text-to-Speech Output (TTS)
Returning the LLM output to audio without sounding robotic poses a major technical hurdle involving localized linguistics. 

- **Unicode Character Polling:** Traditional LLMs output Hindi in English letters (Hinglish), or Hindi natively (Devanagari). Our `tts.py` engine scans the actual returned payload character-by-character against standardized Hex Unicode blocks (`\u0900 -\u097F` for Hindi, `\u0B80-\u0BFF` for Tamil).
- **Target Language Injection:** It automatically detects native Indic scripts and surgically overrides the LLM session global variable, setting the `target_language_code` to `kn-IN`, `ta-IN` etc., in mid-inference.
- **Synthesizer Engine:** Driven by Sarvam's `Bulbul-v2`, it utilizes their highly fluent multi-lingual identity `Hitesh` (Male), ensuring voice persistence regardless of dialogue swapping.
- **Browser Fallback:** The backend encodes generated 16kHz WAV tracks directly into `Base64` transmission JSON packets. If network latency fails the TTS engine, our React layout explicitly fails back asynchronously via `window.speechSynthesis` natively attached to standard browser DOM parameters.

---

## 4. Analytical Intelligence Services 

We run supplementary engines to enrich the raw audio environments beyond just speaking to a user.

### 4.1 AI Reward Engine (RLAIF)
Instead of relying on human QC grading teams, VaakSetu deploys an integrated Reward Evaluator (`reward_engine.py`). Post-session, it leverages the `prometheus-eval/prometheus-7b-v2.0` architecture designed explicitly as a critique model.
1. It grades **Empathy**.
2. It grades **Task Completion**.
3. It performs detailed **Hallucination Detection** comparing the extracted fields directly against transcription data safely housed in SQLite memory chunks.

### 4.2 Local Multi-Speaker Diarization
Conversations are rarely single-speaker. We employ an offline processing mode designed to split combined mono audio files seamlessly into segmented speaker transcripts.
We utilize `pyannote/speaker-diarization-3.1` authenticated natively against Hugging Face. The system calculates vector shifts in the acoustic audio frame, allocating `SPEAKER_00` and `SPEAKER_01` timestamps mapping directly back up to the LangGraph extraction matrix.

---

## 5. Technology Stack Summary

| Technology | Purpose | Utilization Layer |
|------------|---------|-------------------|
| **React / Next.js V15** | Control Dashboard | Control Interfaces / Client MediaRecord |
| **FastAPI** | REST & Socket Framework | Backend Ingestion & Routing |
| **SQLite (aiosqlite)** | Relational Engine | Configurations & RLAIF Tracking |
| **Sarvam AI APIs** | Advanced Indic AI | ASR / LLM conversational matrix / TTS |
| **LangGraph / LangChain** | Inference Chaining | `SmartExtractor` Contextual Execution |
| **Twilio + ngrok** | Telephony Networking | TwiML WebHooks mapping PSTN limits |
| **Hugging Face** | Local ML Architectures | Pyannote Diarization, Prometheus Eval |
| **Pydantic V2** | Code Formatting | Dynamic Data Schemas for Extraction |

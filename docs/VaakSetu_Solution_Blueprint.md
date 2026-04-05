# VaakSetu — Solution Blueprint
### AI-Powered Multilingual Conversational Intelligence Platform
**Team AGNISHAKTI | SRMIST Chennai | Hack2Future 2.0**

---

## GLOSSARY OF ACRONYMS
> Read this first. Every short form used in this document is defined here.

| Acronym | Full Form | Simple Meaning |
|---|---|---|
| **ASR** | Automatic Speech Recognition | Software that converts spoken voice into text |
| **TTS** | Text-to-Speech | Software that converts text into spoken audio |
| **LLM** | Large Language Model | A powerful AI (like ChatGPT) that understands and generates text |
| **NLP** | Natural Language Processing | Teaching computers to understand human language |
| **NER** | Named Entity Recognition | Automatically identifying important words like names, dates, medicines in a sentence |
| **API** | Application Programming Interface | A way for two software programs to talk to each other over the internet |
| **WebSocket** | Web Socket | A two-way, real-time communication channel between a browser and a server |
| **WebRTC** | Web Real-Time Communication | A browser technology that lets you access the microphone and camera |
| **Redis** | Remote Dictionary Server | A super-fast in-memory database used for storing temporary data like chat history |
| **PostgreSQL** | Post-gres Q-L | A reliable relational database (like a structured spreadsheet) that stores permanent records |
| **pgvector** | PostgreSQL Vector Extension | An add-on for PostgreSQL that lets you do AI-powered similarity search |
| **FastAPI** | Fast Application Programming Interface | A modern Python tool for building backend APIs quickly |
| **React** | React.js | A JavaScript library for building interactive web frontends |
| **Docker** | Docker | A tool that packages software so it runs the same on any computer |
| **YAML** | Yet Another Markup Language | A human-readable config file format (like a settings file) |
| **JSON** | JavaScript Object Notation | A common format for structuring data (like a dictionary in Python) |
| **RLAIF** | Reinforcement Learning from AI Feedback | Training an AI to improve itself using scores from another AI as the teacher |
| **DPO** | Direct Preference Optimization | A simpler method to fine-tune an LLM using "good response vs. bad response" pairs |
| **LoRA** | Low-Rank Adaptation | A technique to fine-tune (retrain on new data) a large AI model using very little compute |
| **XLM-RoBERTa** | Cross-lingual Language Model RoBERTa | A multilingual AI model that understands text in 100+ languages |
| **ABDM** | Ayushman Bharat Digital Mission | India's national digital health standard for health records |
| **RBI FAIR** | Reserve Bank of India's Framework for AI Responsibility | India's guidelines for responsible AI in financial services |
| **ASHA** | Accredited Social Health Activist | A trained female community health worker in India |
| **PHC** | Primary Health Centre | A government-run basic healthcare facility at village/block level |
| **ENT** | Ear, Nose, and Throat | A category of medical findings |
| **SFT** | Supervised Fine-Tuning | Training an AI model on labeled examples to improve its task-specific performance |
| **WER** | Word Error Rate | A metric for ASR accuracy — lower is better (0% = perfect transcription) |
| **SDK** | Software Development Kit | A set of ready-made tools and libraries provided by a service (like Twilio) |
| **DTMF** | Dual-Tone Multi-Frequency | The tones your phone keypad makes — used in automated phone systems |
| **OCR** | Optical Character Recognition | AI that reads text from images or scanned documents |
| **VoIP** | Voice over Internet Protocol | Making phone calls over the internet |

---

## SECTION 1 — THE PROBLEM, THE GAP & OUR SOLUTION

### The Core Problem We Are Solving

- India has **1 million+ ASHA and Anganwadi field workers** who document patient health conversations by hand — on paper, inconsistently, and after the fact.
- Every conversation in a multilingual Indian environment switches between **Hindi, Kannada, English, and code-mixed dialects like Hinglish and Kanglish** — sometimes within a single sentence.
- There is no existing, deployable system that simultaneously handles all of: live Indic ASR → context-aware conversation → real-time structured record extraction → multilingual voice response → outbound call automation.
- This problem compounds across sectors: **healthcare**, **NBFC loan verification**, **banking**, **telecom**, and **insurance** — all of which rely on voice interactions but document them manually at massive cost.

### Why Existing Solutions Fail for India

| Existing Tool | Why It Fails |
|---|---|
| Google STT / Azure Speech | Silently drops code-mixed tokens; poor Kannada support; high cloud cost; no Indic TTS pipeline |
| ChatGPT / GPT-4 APIs | English-centric tokenizer (4–6x less efficient for Hindi/Kannada scripts); no Indic ASR or TTS; expensive |
| Dialogflow CX (Google) | Rigid slot-filling that breaks on unstructured speech; no code-mixed intent support; not domain-adaptive |
| Generic call-center bots | No multilingual conversation memory; no structured NER output; no RLAIF alignment |
| Traditional NER tools | Monolingual; completely fail on Romanized Indic and code-mixed input |

### Why Our Solution Is Better

- **Indic-First AI Stack** — Built entirely on open-source Indian AI: AI4Bharat's IndicWhisper ASR (trained on 12,000 hours of real Indian speech across 22 languages), Sarvam-M LLM (24B, +20% over baseline on Indian language benchmarks), and AI4Bharat's Indic-Parler-TTS.
- **Native Code-Mixed Support** — We treat Hinglish and Kanglish as first-class inputs, not translation problems.
- **RLAIF Self-Improvement Loop** — An LLM judge automatically scores every conversation (politeness, accuracy, Indic fluency, policy compliance) and generates preference pairs to fine-tune the agent — no human annotation needed.
- **Zero-Retrain Domain Switching** — One YAML config file swaps the entire extraction schema from healthcare to financial to telecom at runtime. No redeployment, no retraining.
- **Full PDF Compliance** — Every requirement in the problem statement (Voice Layer, ASR, Conversation Engine, Structured Data, Review UI, Longitudinal Dashboard, Healthcare fields, Financial fields) is covered by a dedicated module assigned to a team member.

### Real-World Use Cases

- **Healthcare** — ASHA worker speaks Kannada with a patient → VaakSetu transcribes, extracts symptoms, medications, immunization and pregnancy data → generates ABDM-compatible health record in real time.
- **Financial Services / NBFC** — Automated outbound call to a loan customer in Hinglish → agent verifies identity, collects payment status, amount, mode, reason → logs structured record automatically.
- **Telecom Customer Service** — Inbound multilingual support in Hindi/Tamil/English → intent detection, policy-compliant response, frustrated-customer escalation triggered by sentiment score.
- **E-Commerce / Retail** — Voice-first order queries, complaint registration, return initiation — no typing, in the customer's mother tongue.
- **Banking / Insurance** — Voice-based claim verification with full audit trail for regulatory compliance.

### Full Problem Statement Coverage Checklist

| Requirement from PDF | Covered By |
|---|---|
| Live voice capture (in-person + outbound) | Task 1 (ASR) + Task 4 (Twilio outbound) |
| Multilingual ASR — Kannada, Hindi, English, Code-Mixed | Task 1 |
| Context retention across conversation turns | Task 1 (Redis multi-turn memory) |
| Intent recognition | Task 2 (NLP Pipeline) |
| Dynamic question branching + flow control | Task 1 (Agent YAML config) |
| Structured data extraction — complaint, history, diagnosis, action plan | Task 1 + Task 2 (NER) |
| Editable review interface | Task 3 (React UI) |
| Longitudinal data + dashboard + analytics | Task 3 (React UI) + Task 2 (PostgreSQL) |
| Healthcare workflow fields (symptoms, diagnosis, immunization, pregnancy, ENT, etc.) | Task 1 + Task 2 |
| Financial workflow fields (identity, loan, payment, payer, amount, mode) | Task 1 + Task 2 |
| TTS (multilingual speech synthesis) | Task 4 |
| Outbound call automation | Task 4 |
| Secure storage and retrieval | Task 2 (PostgreSQL) |
| Searchable past interactions | Task 2 + Task 3 |
| RLAIF alignment and reward scoring | Task 1 |

---

## SECTION 2 — IMPLEMENTATION GUIDE FOR TEAM AGNISHAKTI

> **To Shaurya (main branch):** This section is your operational playbook. Read every task guide before coding begins. Assign tasks, enforce the GitHub workflow, and review all pull requests.
>
> **To all team members:** You are all beginners. This guide does not ask you to memorize code. It tells you exactly what to build, what tools to use, what the expected output looks like, and how to collaborate. Follow it step by step and you will have a working system.

---

## TEAM & TASK ASSIGNMENTS

Tasks are assigned in **decreasing order of difficulty**. The most complex goes to Shaurya, the simplest to Mouriyan.

| Priority | Task | Owner | 
|---|---|---|
| **Task 1** | AI Core — ASR Pipeline + Dialogue Agent + RLAIF Reward Engine | **Shaurya Kesarwani** | 
| **Task 2** | Backend — FastAPI Server + NLP Pipeline + Database | **Sudhanshu Kumar** | 
| **Task 3** | Frontend — React UI + Dashboard + Review Interface | **Md Nayaj** | 
| **Task 4** | Output Layer — TTS + Outbound Calls + Customer Simulation | **Mouriyan** | 

---

## GITHUB COLLABORATION WORKFLOW

> This is how all four of you will work together without overwriting each other's code. Follow every step in order.

### What is GitHub? (For Beginners)
GitHub is a website where you store your code online, track all changes made to it, and collaborate with teammates. Think of it like Google Docs for code — everyone works on their own copy, and changes are merged together safely.

### Key Terms You Must Know

| Term | Meaning |
|---|---|
| **Repository (Repo)** | Your project's folder stored on GitHub |
| **Clone** | Downloading a copy of the GitHub repo to your own computer |
| **Branch** | A separate version of the project where you work without affecting others |
| **Commit** | Saving your changes with a short description message |
| **Push** | Uploading your saved changes from your computer to GitHub |
| **Pull Request (PR)** | A formal request for Shaurya to review and merge your branch into the main project |
| **Merge** | Combining your branch's changes into the main project |
| **main branch** | The official, stable version of the project — only Shaurya merges into this |

---

### Step-by-Step GitHub Workflow

#### STEP 0 — Shaurya Sets Up the Repository (Do This First, Before Anyone Else Starts)

Shaurya will:
1. Create a new GitHub repository named `vaaksetu` — set it to **Public**.
2. Create the complete folder structure (described below) and push it to the `main` branch.
3. Add the following **prerequisite files** to the repo before tagging others to begin:
   - `.env.example` — A template file listing all required API keys (actual values NOT included — never push real keys to GitHub)
   - `requirements.txt` — A text file listing all Python packages the project needs
   - `README.md` — A short description of the project, how to set it up, and which folders belong to whom
   - `docker-compose.yml` — A configuration file that starts Redis and PostgreSQL with one command
   - `configs/healthcare.yaml` — The healthcare domain configuration file
   - `configs/financial.yaml` — The financial domain configuration file
4. Invite all three teammates as **collaborators** on the GitHub repository.
5. Notify everyone on WhatsApp once this is done: *"Repo is ready. Clone it now."*

---

#### STEP 1 — Everyone Clones the Repo (Day 1, After Shaurya's Setup)

Every team member opens their terminal and runs:
```
git clone https://github.com/AGNISHAKTI/vaaksetu.git
cd vaaksetu
```
This downloads the full project folder to their computer.

---

#### STEP 2 — Each Member Creates Their Own Branch

Before starting any work, each person creates a personal branch named after their task:

| Member | Branch Name Command to Run |
|---|---|
| Shaurya | `git checkout -b task1-ai-core` |
| Sudhanshu | `git checkout -b task2-backend` |
| Nayaj | `git checkout -b task3-frontend` |
| Mouriyan | `git checkout -b task4-output-layer` |

**Rule:** Never work directly on `main`. Always work on your own branch.

---

#### STEP 3 — Each Member Works in Their Own Folder

Every team member creates files only inside their designated folder (see the folder structure below). Do not touch any other folder.

---

#### STEP 4 — Save Work Regularly with Commits

Every 1–2 hours of work, each member should save their progress to GitHub:

```
git add .
git commit -m "Short description of what you did — e.g. Added sentiment classifier"
git push origin your-branch-name
```

This ensures your work is backed up and visible to Shaurya.

---

#### STEP 5 — Create a Pull Request When Your Task Is Done

When a member finishes their task:
1. Go to the GitHub website → the `vaaksetu` repository.
2. Click the **"Compare & pull request"** button that appears for your branch.
3. Write a short description: *"Task 2 complete — FastAPI backend with all endpoints working, database initialized."*
4. Tag **Shaurya** as the reviewer.
5. Click **"Create pull request"**.

---

#### STEP 6 — Shaurya Reviews and Merges

Shaurya will:
1. Review the PR — look at the files changed.
2. Test the new code locally by pulling the branch:
   ```
   git fetch origin
   git checkout task2-backend
   ```
3. If it works: click **"Merge pull request"** on GitHub.
4. If there's a problem: leave a comment on the PR explaining what needs to be fixed. The member fixes it, commits again, and the PR updates automatically.

---

#### STEP 7 — Everyone Syncs After Each Merge

After Shaurya merges a PR, every team member updates their local copy:
```
git checkout main
git pull origin main
git checkout your-branch-name
git merge main
```
This ensures everyone has the latest merged code.

---

### Golden Rules

1. 🔴 **Never push directly to `main`** — always use a branch and PR.
2. 🟡 **Commit often** — small saves are better than one giant commit at the end.
3. 🟢 **Communicate on WhatsApp** before modifying any shared file.
4. 🔵 **If you get a "merge conflict"** (two people changed the same line) — call Shaurya immediately, don't try to resolve it yourself.

---

## FINAL PROJECT FOLDER STRUCTURE

This is exactly how the project folder will be organized once all four PRs are merged.

```
vaaksetu/
│
├── .env.example                  ← Template for environment variables (no real keys here)
├── .gitignore                    ← Tells Git to ignore sensitive files like .env
├── README.md                     ← Project overview and setup instructions
├── requirements.txt              ← All Python packages needed (pip install -r requirements.txt)
├── docker-compose.yml            ← Starts Redis and PostgreSQL with one command
│
├── configs/                      ← Domain configuration files (Shaurya's responsibility)
│   ├── healthcare.yaml           ← All healthcare field definitions and agent prompts
│   └── financial.yaml            ← All financial field definitions and agent prompts
│
├── task1_ai_core/                ← SHAURYA'S FOLDER
│   ├── README.md                 ← What this module does, how to run it
│   ├── asr.py                    ← ASR module (Sarvam STT API + IndicWhisper fallback)
│   ├── agent.py                  ← Dialogue agent (Sarvam-M + Redis memory + YAML config loader)
│   └── reward_engine.py          ← RLAIF scoring (programmatic + LLM judge + combined reward)
│
├── task2_backend/                ← SUDHANSHU'S FOLDER
│   ├── README.md                 ← What this module does, how to run it
│   ├── main.py                   ← FastAPI app — all REST and WebSocket endpoints
│   ├── nlp_pipeline.py           ← Sentiment classifier + NER extractor + intent detector
│   ├── database.py               ← PostgreSQL connection, table creation, save/retrieve records
│   └── models.py                 ← Python data models for sessions, turns, records (Pydantic)
│
├── task3_frontend/               ← NAYAJ'S FOLDER
│   ├── README.md                 ← What this module does, how to run it
│   └── src/
│       ├── App.tsx               ← Root React component and routing
│       ├── pages/
│       │   ├── SessionStart.tsx  ← Domain selector and session initiation page
│       │   ├── ChatWindow.tsx    ← Live conversation page with WebSocket connection
│       │   ├── RecordViewer.tsx  ← Structured record display and edit page
│       │   └── Dashboard.tsx     ← Historical sessions, analytics, search
│       └── components/
│           ├── SentimentBar.tsx  ← Real-time sentiment color indicator
│           ├── EntityPanel.tsx   ← Right sidebar showing collected fields with tick marks
│           ├── ScoreCard.tsx     ← RLAIF reward score display after session ends
│           └── AudioRecorder.tsx ← WebRTC microphone capture component
│
├── task4_output_layer/           ← MOURIYAN'S FOLDER
│   ├── README.md                 ← What this module does, how to run it
│   ├── tts.py                    ← Text-to-Speech using Sarvam TTS API
│   ├── outbound_call.py          ← Twilio outbound call automation
│   └── simulation.py             ← Automated customer persona simulation for testing
│
└── tests/                        ← Integration tests (Shaurya writes after all PRs are merged)
    └── test_full_pipeline.py     ← End-to-end test: voice in → structured record out
```

---

## TASK 1 — AI CORE (Shaurya Kesarwani)

> **You are building the brain of VaakSetu.** This task is the hardest and most critical. Everything else depends on this working correctly. You have three sub-components to build: the ASR pipeline, the Dialogue Agent, and the RLAIF Reward Engine.

---

### Sub-Task 1A — Automatic Speech Recognition (ASR) Pipeline

#### What This Does
Converts live spoken audio (in Hindi, Kannada, English, or any mix of them) into clean, structured text that the rest of the system can understand.

#### Architecture

```
[Microphone / Twilio Audio Stream]
           │
           ▼
  [Audio Pre-processing]
  - Convert to 16kHz mono WAV format
  - Normalize volume levels
           │
           ▼
  [Primary ASR: Sarvam STT API]
  - Model: saaras:v2
  - Supports: hi-IN (Hindi), kn-IN (Kannada), en-IN (English)
  - Code-mixed input: send as hi-IN or kn-IN — model handles mixing natively
           │
           ▼ (if Sarvam API fails or is unavailable)
  [Fallback ASR: AI4Bharat IndicWhisper]
  - Model: ai4bharat/indicwhisper-medium (via HuggingFace)
  - Downloaded once, runs locally on the laptop
  - Slower but free and works offline
           │
           ▼
  [Language Identification]
  - AI4Bharat IndicLID model
  - Tags each segment: is this Hindi, Kannada, English, or code-mixed?
           │
           ▼
  OUTPUT: { "transcript": "Mujhe bukhar hai", "language": "hi-IN", "confidence": 0.95 }
```

#### Tools and Technology

| Tool | What It Is | Why We Use It |
|---|---|---|
| **Sarvam STT API** | Cloud ASR service by Sarvam AI | Trained on Indian speech; streaming capable; free tier available |
| **AI4Bharat IndicWhisper** | Open-source Indic ASR model (HuggingFace) | 12,000 hours of Indian voice data; supports all 22 official languages |
| **sounddevice** | Python library | Records audio from the microphone in real time |
| **soundfile** | Python library | Reads and writes audio files (WAV format) |
| **httpx** | Python library | Makes fast async (non-blocking) API calls to Sarvam |

#### How to Get the Sarvam API Key
1. Go to: `https://dashboard.sarvam.ai`
2. Create a free account.
3. Navigate to API Keys → Generate New Key.
4. Copy the key and paste it into your `.env` file as `SARVAM_API_KEY=your_key_here`.

#### Expected Output After This Sub-Task
- Running `python task1_ai_core/asr.py` records 5 seconds of your voice.
- The terminal prints the transcript in the language you spoke.
- Test with: Hindi sentence, a Kannada sentence, and a Hinglish mix.

---

### Sub-Task 1B — Dialogue Agent (Conversation Manager)

#### What This Does
This is the AI that talks back. Given a user's transcript, it maintains conversation context across multiple turns, understands what information it still needs to collect, and generates a helpful response in the same language the user spoke.

#### Architecture

```
[Incoming Transcript + Sentiment Score + Entities from Task 2]
           │
           ▼
  [Redis Context Lookup]
  - Key: "session:{session_id}:history"
  - Fetches the last 10 messages of this conversation
  - If new session: loads the domain greeting from YAML config
           │
           ▼
  [Domain Config Loader (YAML)]
  - Reads configs/healthcare.yaml or configs/financial.yaml
  - Contains: agent name, required fields, system prompt template, greeting text
  - Calculates which fields are still missing ("collected vs required")
           │
           ▼
  [System Prompt Construction]
  - Combines: domain instructions + missing fields list + conversation history
  - Tells the LLM: "You need to collect [symptom, age, duration]. You have [name] so far."
           │
           ▼
  [Sarvam-M LLM Call (via Sarvam Chat API)]
  - Model: sarvam-m
  - Mode: non-think (faster, good for conversation)
  - Temperature: 0.7 (some creativity, not too random)
  - Max tokens: 256 (keep responses short and conversational)
           │
           ▼
  [Response Saved to Redis]
  - The agent's reply is appended to conversation history
  - History expires after 1 hour (to free memory)
           │
           ▼
  OUTPUT: { "response": "Ramesh ji, aapko kab se bukhar hai?", "is_complete": false }
```

#### Healthcare YAML Config — Required Fields
The agent must collect all of these for a healthcare session to be marked "complete":
- patient_name, age, gender
- symptoms, symptom_duration
- past_medical_history
- current_medications, allergies
- clinical_observations (what the ASHA worker observes)
- diagnosis_classification
- treatment_advice
- immunization_status
- pregnancy_status (if applicable)
- risk_indicators
- injury_details, mobility_status
- ent_findings (ear, nose, throat examination notes)

#### Financial YAML Config — Required Fields
- customer_name, customer_id
- loan_id, account_number
- identity_verified (yes/no)
- payment_status (paid / pending / partial)
- amount_paid
- payment_date
- payment_mode (UPI / cash / cheque / NEFT / RTGS)
- payer_identity (self / family / employer)
- reason_for_payment_delay (if pending)
- executive_interaction_notes

#### Tools and Technology

| Tool | What It Is | Why We Use It |
|---|---|---|
| **Sarvam-M via Sarvam Chat API** | Indic LLM, 24B parameters, OpenAI-compatible | +20% on Indian language benchmarks; supports Hindi, Kannada, Hinglish natively |
| **Redis (redis-py)** | In-memory database | Sub-millisecond storage and retrieval of conversation turns |
| **PyYAML** | Python library | Reads YAML config files easily |
| **python-dotenv** | Python library | Loads API keys from the `.env` file |

#### How to Get the Sarvam Chat API Key
Same key as the ASR above — one `SARVAM_API_KEY` works for all Sarvam services.

#### Expected Output After This Sub-Task
- A conversation that lasts multiple turns.
- The agent asks one question at a time, in the same language the user speaks.
- The agent stops when all required fields are collected.
- Test: simulate a 6-turn healthcare conversation by typing responses in the terminal.

---

### Sub-Task 1C — RLAIF Reward Engine

#### What This Does
After a conversation finishes, this module automatically scores it — like a quality checker. It combines a fast rule-based score with an LLM judge score to decide whether the conversation was good (a "winning" response to learn from) or bad (a "losing" response to avoid).

This is the novel research contribution of VaakSetu. It is what makes our system self-improving and aligns directly with the "LLM Scoring" requirement in the problem statement.

#### What Is RLAIF? (Simple Explanation)
Imagine you are a student. Every time you answer a question:
- A rule-checker marks you on speed and accuracy automatically.
- A teacher (the LLM judge) reads your full answer and rates it on politeness, correctness, and language quality.
- Combined, these scores tell you: was this a good answer or a bad one?
- Over time, you learn to give better answers. That is RLAIF — but for an AI agent.

#### Architecture

```
[Completed Conversation History (list of turns)]
           │
           ├──────────────────────────────────────────┐
           ▼                                          ▼
  [Programmatic Scorer]                    [LLM Judge Scorer]
  Fast, rule-based, no API call            OpenAI gpt4o API
                                           (cheapest, fastest model)
  Scores:                                  Scores (1–5 each):
  • Resolution time (fewer turns = better) • Politeness
  • Sentiment improvement (start vs end)   • Accuracy (correct info, no hallucinations)
  • Turn efficiency (4–8 turns ideal)      • Indic fluency (natural Hinglish/Kannada)
  • Self-service rate (no escalation)      • Policy compliance (no medical advice given)
  • Content safety check                   • Resolution quality (did it achieve the goal?)
           │                                          │
           └──────────────────┬───────────────────────┘
                              ▼
                  [Combined Reward Score]
                  Formula: (LLM score × 60%) + (Programmatic score × 40%)
                  Range: 0.0 to 1.0
                              │
                              ▼
                  [DPO Label Assignment]
                  Score ≥ 0.70 → label: "chosen" (winning response)
                  Score < 0.70 → label: "rejected" (losing response)
                              │
                              ▼
                  OUTPUT: Full score JSON with all dimension scores,
                          combined reward, DPO label, and improvement feedback
```

#### Tools and Technology

| Tool | What It Is | Why We Use It |
|---|---|---|
| **OpenAI gpt4o API** | openai model | Perfect for LLM judging — structured JSON output, low cost per call |
| **OpenAi (Python library)** | Official Python SDK for openai | Makes calling openai straightforward |
| **Custom Python logic** | Your own code | Calculates programmatic scores based on conversation metadata |



#### Expected Output After This Sub-Task
Running the reward engine on a sample conversation prints a JSON like:
```
{
  "programmatic": { "time_score": 0.85, "sentiment_score": 0.72, "turn_score": 1.0, ... },
  "llm_judge": { "politeness": 4, "accuracy": 5, "indic_fluency": 4, "overall": 4.2, "feedback": "..." },
  "combined_reward": 0.79,
  "dpo_label": "chosen"
}
```

---

## TASK 2 — BACKEND (Sudhanshu Kumar)

> **You are building the spine of VaakSetu.** Your job is to create the server that connects the AI core (Task 1) to the frontend (Task 3), store all data permanently, and run the NLP pipeline (sentiment, entities, intent). Everything flows through your API.

---

### What Is a Backend? (For Beginners)
A backend is a server — a program that runs in the background and waits for requests. When the frontend asks "start a new session", the backend handles it. When Task 1 sends a transcript, the backend saves it. Think of it as the kitchen of a restaurant — the user sees the dining hall (frontend), but all the cooking happens in the back.

---

### Sub-Task 2A — NLP Pipeline (Natural Language Processing)

#### What This Does
Takes the raw text transcript from Task 1 and extracts three things:
1. **Sentiment** — Is the speaker angry, neutral, or happy?
2. **Intent** — What does the speaker want? (paying, complaining, asking a question?)
3. **Named Entities** — What specific information did they mention? (medicines, loan IDs, dates, amounts)

#### Architecture

```
[Raw Text Transcript: "Mujhe teen din se bukhar hai aur khansi bhi ho rahi hai"]
           │
           ├─────────────────────────────────────────────────────┐
           │                                                     │
           ▼                                                     ▼
  [Sentiment Classifier]                             [Intent Detector]
  Model: XLM-RoBERTa                                 Simple keyword matching
  (cardiffnlp/twitter-xlm-roberta-base-sentiment)   "pay" → payment intent
  Works on code-mixed text natively                 "problem" → complaint intent
  Output: negative / neutral / positive + score     "kya" → query intent
  Score < 0.35 → flag as "frustrated"              Output: { "intent": "healthcare" }
           │
           ▼
  [Named Entity Recognizer (NER)]
  Two layers:
  1. spaCy (standard NER) → finds: person names, dates, locations, organizations
  2. Custom Keyword Patterns (domain-specific) →
     Healthcare: finds symptoms, medicines, durations, pregnancy keywords
     Financial: finds loan IDs (regex), rupee amounts, payment modes, UPI IDs
  Output: { "symptoms": ["bukhar", "khansi"], "duration": ["teen din"] }
           │
           ▼
  FINAL OUTPUT: {
    "sentiment": { "label": "neutral", "score": 0.55, "is_frustrated": false },
    "intent": "healthcare",
    "entities": { "symptoms": ["bukhar", "khansi"], "duration": ["teen din"] }
  }
```

#### Tools and Technology

| Tool | What It Is | Why We Use It |
|---|---|---|
| **XLM-RoBERTa** | Cross-lingual AI model (HuggingFace) | Understands code-mixed text; pre-trained on 100+ languages |
| **spaCy 3.7** | NLP library for Python | Fast, lightweight NER; runs without GPU |
| **transformers** | HuggingFace Python library | Loads pre-trained AI models like XLM-RoBERTa |
| **re (Python built-in)** | Regular Expression library | Pattern matching for loan IDs, phone numbers, amounts |

#### Expected Output After This Sub-Task
- Input any Hindi, Kannada, or Hinglish sentence.
- Terminal prints sentiment, intent, and extracted entities correctly.
- Test with 5 sample sentences: 2 healthcare, 2 financial, 1 English.

---

### Sub-Task 2B — FastAPI Server (The API Layer)

#### What This Does
Creates the central server with all endpoints. Think of endpoints as doors in a building — each door handles a specific request. The frontend knocks on `/api/session/start` to begin a conversation, knocks on `/api/turn/text` to send a message, and knocks on `/api/session/{id}/record` to get the final structured data.

#### All Endpoints You Need to Build

| Endpoint | Method | What It Does |
|---|---|---|
| `/api/session/start` | POST | Creates a new conversation session, returns session ID |
| `/api/turn/text` | POST | Processes one conversation turn (text input); returns agent response + sentiment + entities |
| `/api/session/{id}/record` | GET | Returns the structured record (all collected fields) for a session |
| `/api/session/{id}/score` | GET | Runs RLAIF scoring on a completed session |
| `/api/sessions/list` | GET | Returns all past sessions for the dashboard |
| `/api/session/{id}/history` | GET | Returns the full conversation transcript for a session |
| `/ws/{session_id}` | WebSocket | Real-time bidirectional channel for the live chat interface |

#### Architecture

```
[Frontend / Browser]
        │  HTTP Request or WebSocket message
        ▼
[FastAPI Server — main.py]
        │
        ├── Calls Task 1 functions: transcribe(), agent.respond(), reward_engine.score()
        ├── Calls Task 2 functions: get_sentiment(), extract_entities(), analyze_intent()
        ├── Calls Task 4 functions: text_to_speech()
        └── Calls database.py functions: save_session(), save_turn(), get_record()
        │
        ▼
[Returns JSON response to Frontend]
```

#### Tools and Technology

| Tool | What It Is | Why We Use It |
|---|---|---|
| **FastAPI** | Python web framework | Auto-generates API documentation; async-native; very fast |
| **uvicorn** | ASGI server | Runs the FastAPI app; supports WebSockets |
| **Pydantic** | Python data validation library | Ensures incoming request data is in the correct format |
| **CORS Middleware** | FastAPI built-in | Allows the React frontend (port 3000) to call the backend (port 8000) |

#### Expected Output After This Sub-Task
- Run `uvicorn task2_backend.main:app --reload --port 8000`.
- Open browser at `http://localhost:8000/docs` → see interactive API documentation (auto-generated by FastAPI).
- Successfully call `/api/session/start` via the docs page and receive a session ID.

---

### Sub-Task 2C — Database Layer (PostgreSQL + pgvector)

#### What This Does
Permanently stores all sessions, conversation turns, structured records, and reward scores. Also enables semantic (meaning-based) search over historical records using pgvector.

#### Database Schema (Tables You Need to Create)

**Table 1: `sessions`**
Stores one row per conversation session.
- `id` — unique session identifier (UUID format)
- `domain` — "healthcare" or "financial"
- `created_at` — timestamp when session started
- `completed_at` — timestamp when all required fields were collected
- `status` — "active" / "complete" / "abandoned"
- `structured_record` — the final collected fields (stored as JSON)
- `reward_score` — the RLAIF combined reward score (decimal number)

**Table 2: `turns`**
Stores one row per conversation message exchange.
- `id` — auto-incrementing number
- `session_id` — links to the sessions table
- `turn_number` — 1, 2, 3, etc.
- `user_transcript` — what the user said (text)
- `agent_response` — what the agent replied (text)
- `sentiment_score` — decimal from 0.0 to 1.0
- `intent` — detected intent string
- `entities` — extracted entities (stored as JSON)
- `created_at` — timestamp

**Table 3: `record_embeddings`**
Stores vector embeddings for semantic search (powered by pgvector).
- `id` — auto-incrementing number
- `session_id` — links to sessions
- `embedding` — 384-dimensional vector (created by SentenceTransformer)
- Enables searching past records by meaning, not just exact keywords

#### Tools and Technology

| Tool | What It Is | Why We Use It |
|---|---|---|
| **PostgreSQL 16** | Relational database | Reliable, structured storage for all session and turn data |
| **pgvector extension** | PostgreSQL add-on | Adds vector search capability for semantic history lookup |
| **psycopg2** | Python PostgreSQL driver | Lets Python code talk to PostgreSQL |
| **Docker** | Containerization | Runs PostgreSQL with one command (`docker-compose up`) |
| **sentence-transformers** | Python library | Converts text to numerical vectors for semantic search |

#### Expected Output After This Sub-Task
- A `sessions` table and `turns` table exist in the database.
- After a test conversation, one row appears in `sessions` and multiple rows appear in `turns`.
- Querying by `session_id` returns the full conversation history.

---

## TASK 3 — FRONTEND (Md Nayaj)

> **You are building everything the user sees and touches.** Your job is to create a clean, professional web interface using React. It has four screens: session setup, live chat, structured record view, and a historical dashboard. You do not need to understand the AI — you just need to display data received from the backend API.

---

### What Is React? (For Beginners)
React is a JavaScript library that helps you build interactive websites. Instead of building one giant HTML page, you build small reusable "components" (like Lego bricks) and assemble them into screens. When data changes (like a new message arriving), React automatically updates only the part of the screen that needs to change.

---

### The Four Screens You Need to Build

#### Screen 1 — Session Start (`SessionStart.tsx`)

**What it looks like:**
- A centered card with the VaakSetu logo at the top.
- Two large buttons: **"Healthcare"** and **"Financial Services"** — user clicks one to choose the domain.
- A "Start Conversation" button.
- When clicked: calls `POST /api/session/start` → receives `session_id` → navigates to Screen 2.

**Components on this screen:**
- Domain selector (two styled cards, one highlights when selected)
- Start button (disabled until a domain is chosen)
- Loading spinner while the API call is in progress

---

#### Screen 2 — Live Chat (`ChatWindow.tsx`)

**What it looks like:**
- Left side (60% width): Chat bubbles — user messages on the right (blue), agent messages on the left (dark).
- Right side (40% width): Entity Panel — a vertical list of all required fields, turning green with a ✓ as they are collected.
- Top bar: Sentiment indicator strip — color changes from red → yellow → green as the conversation progresses.
- Bottom: Text input box + Send button (for now; mic support is in `AudioRecorder.tsx`).

**How real-time works:**
- Connect to `WebSocket at /ws/{session_id}` when the screen loads.
- Every message sent → immediately shows in the chat bubble.
- Every response received via WebSocket → appears as agent bubble.
- Sentiment score in the response → updates the top color strip.
- Entities in the response → ticks off the corresponding field in the Entity Panel.
- When `is_complete = true` arrives → show a "View Record" button that navigates to Screen 3.

**Components on this screen:**
- `MessageBubble.tsx` — single chat message, styled differently for user vs agent
- `SentimentBar.tsx` — horizontal strip at the top; red (#EF4444), yellow (#F59E0B), green (#10B981)
- `EntityPanel.tsx` — right sidebar listing all fields; each shows a grey dot (missing) or green tick (collected)
- `AudioRecorder.tsx` — a microphone button that uses WebRTC `getUserMedia` to record audio

---

#### Screen 3 — Structured Record Viewer (`RecordViewer.tsx`)

**What it looks like:**
- A clean, printable form layout showing all collected fields.
- Each field is editable (clicking turns it into a text input).
- An "Approve Record" button — saves final edits back to the database.
- A "Score Conversation" button — calls `GET /api/session/{id}/score` and reveals the ScoreCard below.
- ScoreCard shows: LLM judge scores (politeness, accuracy, fluency, policy), combined reward, and a short feedback text.

**Components on this screen:**
- `FieldRow.tsx` — a label + value pair, clicking value makes it editable
- `ScoreCard.tsx` — a card with colored score bars for each dimension (1–5 scale)
- `ExportButton.tsx` — downloads the record as a PDF (use `react-to-pdf` library)

---

#### Screen 4 — Historical Dashboard (`Dashboard.tsx`)

**What it looks like:**
- A search bar at the top — type a patient name, loan ID, symptom, etc. → results appear below.
- A table of past sessions showing: date, domain, status (complete / active), reward score, patient/customer name.
- Clicking any row opens Screen 3 (Record Viewer) for that session.
- Summary stats at the top: total sessions today, average reward score, % completed sessions.

**How search works:**
- Call `GET /api/sessions/list?search=ramesh` → backend searches PostgreSQL and returns matches.

---

### Tools and Technology

| Tool | What It Is | Why We Use It |
|---|---|---|
| **React 18** | JavaScript UI library | Component-based, fast, widely used |
| **TypeScript** | Typed JavaScript | Catches bugs earlier; better code suggestions in editor |
| **Tailwind CSS** | Utility-first CSS framework | Fast styling without writing custom CSS files |
| **axios** | HTTP client for JavaScript | Makes API calls to the FastAPI backend cleanly |
| **react-router-dom** | Routing library | Handles navigation between the 4 screens without page reloads |
| **WebSocket (browser built-in)** | Real-time communication | Connects to `/ws/{session_id}` for live chat |
| **WebRTC getUserMedia** | Browser API | Accesses the microphone for audio recording |
| **react-to-pdf** | PDF export library | Lets the user download the structured record as a PDF |

#### Expected Output After This Task
- `npm start` opens the browser at `http://localhost:3000`.
- All four screens are navigable.
- The chat screen connects to the backend via WebSocket and displays live messages.
- The Entity Panel updates as the conversation progresses.
- The Record Viewer shows and allows editing of collected fields.
- The Dashboard shows a table of past sessions.

---

## TASK 4 — OUTPUT LAYER (Mouriyan)

> **You are building the voice output and testing engine of VaakSetu.** This is the most beginner-friendly task. You have three parts: the Text-to-Speech module (so the agent can speak back), the outbound call automation (using Twilio), and the customer simulation scripts (for automated testing).

---

### Sub-Task 4A — Text-to-Speech (TTS)

#### What This Does
Converts the agent's text response into spoken audio in the correct Indian language. The audio is played back to the user (for in-person mode) or streamed into a phone call (for outbound mode).

#### Architecture

```
[Agent Response Text: "Ramesh ji, aapko kab se bukhar hai?"]
           │
           ▼
  [Sarvam TTS API]
  - Endpoint: https://api.sarvam.ai/text-to-speech
  - Input: text, target_language_code (hi-IN / kn-IN / en-IN), speaker name
  - Output: audio encoded in base64 format
           │
           ▼
  [Base64 Decode → WAV audio bytes]
           │
           ▼
  [Play via sounddevice (in-person)] OR [Stream to Twilio call (outbound)]
```

#### Available Voices (Sarvam TTS)
- Hindi: `meera` (female), `arjun` (male)
- Kannada: `neelan` (male)
- Tamil: `pavithra` (female)
- English (Indian accent): `maya` (female)

#### Tools and Technology

| Tool | What It Is | Why We Use It |
|---|---|---|
| **Sarvam TTS API** | Cloud Text-to-Speech by Sarvam AI | Natural Indian-accent voices; 18 languages; same API key as ASR |
| **sounddevice** | Python library | Plays audio through the laptop speakers |
| **soundfile** | Python library | Converts audio bytes to the right format for playback |
| **base64** | Python built-in | Decodes the audio data returned by the API |

#### Expected Output After This Sub-Task
- Run `python task4_output_layer/tts.py`.
- The laptop speaks "Namaste! Main Aarogya Sahayak hoon." in a clear Hindi voice.
- Test with one Hindi and one Kannada sentence.

---

### Sub-Task 4B — Outbound Call Automation (Twilio)

#### What This Does
Places an automated phone call to a number, plays a greeting, listens to the response (speech), and routes it back to the VaakSetu pipeline. This covers the "Automated outbound call handling" requirement in the PDF.

#### How Twilio Works (Simple Explanation)
Twilio is a company that gives you programmable phone call capabilities via an API. You tell Twilio: "call this number, say this, wait for a response, send the audio to my server." Twilio handles all the telephony complexity — you just write Python code.

#### Architecture

```
[Your Python Code triggers Twilio API]
           │
           ▼
  [Twilio Places Outbound Call to Customer Phone Number]
           │
           ▼
  [Customer Picks Up → Twilio plays TTS greeting]
           │
           ▼
  [Customer Speaks → Twilio records audio]
           │
           ▼
  [Twilio sends audio to your server webhook URL]
           │
           ▼
  [Your server passes audio to Task 1 ASR pipeline]
           │
           ▼
  [Agent processes, generates response → TTS → Twilio plays it back]
           │
           (loop continues until conversation is complete)
```

#### What You Need to Set Up Twilio
1. Go to `https://twilio.com` → Sign Up → Free Trial.
2. You get `$15.00` credit — enough for ~150 minutes of calls.
3. From the Twilio Console, copy:
   - `TWILIO_ACCOUNT_SID` → paste into `.env`
   - `TWILIO_AUTH_TOKEN` → paste into `.env`
4. Buy a Twilio phone number (free with trial) → copy it as `TWILIO_PHONE_NUMBER` in `.env`.
5. Use **ngrok** (`https://ngrok.com`) to expose your local server to the internet so Twilio can send audio to it.
   - Install ngrok → run: `ngrok http 8000`
   - Copy the public URL (looks like `https://abc123.ngrok.io`) → set it as your Twilio webhook URL.

#### Tools and Technology

| Tool | What It Is | Why We Use It |
|---|---|---|
| **Twilio Python SDK** | Official Twilio library | Simplifies making calls, handling audio streams, DTMF |
| **ngrok** | Tunneling tool | Exposes your local server to the internet for Twilio webhooks |
| **TwiML** | Twilio Markup Language | XML-like instructions that tell Twilio how to handle a call |
| **httpx** | Python library | Handles async webhook requests from Twilio |

#### Expected Output After This Sub-Task
- Running `python task4_output_layer/outbound_call.py` places a real call to a test number.
- The call plays a Hindi greeting.
- You speak a response → it transcribes → the agent responds → you hear the agent's voice.

---

### Sub-Task 4C — Customer Simulation Engine

#### What This Does
Simulates different types of customers (angry, polite, confused, evasive) having conversations with the agent automatically — without needing a real person. This is used for testing the full pipeline and generating scored data for the RLAIF reward engine.

#### Four Customer Personas to Simulate

| Persona | Language | Personality | Starting Message |
|---|---|---|---|
| Frustrated Hindi Speaker | Hinglish | Angry, impatient, short sentences | "Mujhe bahut problem ho rahi hai!" |
| Polite Kannada Speaker | Kannada + English | Soft-spoken, cooperative | "Excuse me, can you help? Nange help beku iddhe" |
| Elderly Hindi Patient | Formal Hindi | Confused, slow, repeats | "Namaste bete, mujhe samajh nahi aa raha..." |
| Evasive Loan Customer | Hinglish | Avoids questions, vague | "Bhai abhi payment nahi ho sakti..." |

#### Architecture

```
For each persona:
  1. Start a new session via POST /api/session/start
  2. Send the seed message via POST /api/turn/text
  3. Print the agent's response
  4. Pick a realistic follow-up message from a predefined list
  5. Repeat until is_complete = true or max 10 turns
  6. Call GET /api/session/{id}/score to get the reward score
  7. Print a summary: persona name, turns taken, reward score, DPO label
```

#### Expected Output After This Sub-Task
- Running `python task4_output_layer/simulation.py` automatically runs 2 personas.
- The terminal shows the full conversation transcript for each persona.
- Each conversation ends with a printed reward score and DPO label.
- This output can be shown live during the hackathon demo as proof of the self-evaluation loop.

#### Tools and Technology

| Tool | What It Is | Why We Use It |
|---|---|---|
| **httpx** | Python HTTP library | Makes API calls to your own FastAPI server |
| **asyncio** | Python async library | Runs multiple simulations concurrently |
| **random** | Python built-in | Picks varied follow-up messages to avoid repetitive scripts |

---

## SYSTEM ARCHITECTURE — FULL PICTURE

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                          VaakSetu — Complete System                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

  [USER — ASHA Worker / NBFC Agent / Customer]
          │
          ├── In-Person Mode: Microphone via WebRTC (Browser)
          └── Outbound Mode: Phone Call via Twilio
          │
          ▼
  ┌─────────────────────────────┐
  │   TASK 1 — AI CORE          │  (Shaurya)
  │                             │
  │  ASR Pipeline               │ ← Sarvam STT API (primary)
  │  (Kannada/Hindi/English/    │ ← AI4Bharat IndicWhisper (fallback)
  │   Code-Mixed)               │
  │         │                   │
  │         ▼                   │
  │  Dialogue Agent             │ ← Sarvam-M LLM (24B)
  │  + Redis Multi-Turn Memory  │ ← YAML Domain Config (healthcare/financial)
  │  + YAML Domain Switching    │
  │         │                   │
  │         ▼                   │
  │  RLAIF Reward Engine        │ ← Programmatic Scorer
  │  (LLM Judge + Programmatic) │ ← openai gpt-4o  (LLM Judge)
  └────────────┬────────────────┘
               │
               ▼
  ┌─────────────────────────────┐
  │   TASK 2 — BACKEND          │  (Sudhanshu)
  │                             │
  │  NLP Pipeline               │ ← XLM-RoBERTa (Sentiment)
  │  (Sentiment + NER + Intent) │ ← spaCy + Custom Patterns (NER)
  │         │                   │
  │         ▼                   │
  │  FastAPI Server             │ ← REST Endpoints + WebSocket
  │  (All API Endpoints)        │
  │         │                   │
  │         ▼                   │
  │  Database Layer             │ ← PostgreSQL + pgvector
  │  (Sessions, Turns, Records) │
  └────────────┬────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
  ┌────────────┐  ┌──────────────────────────┐
  │  TASK 3    │  │  TASK 4 — OUTPUT LAYER   │  (Mouriyan)
  │  FRONTEND  │  │                          │
  │  (Nayaj)   │  │  TTS Response            │ ← Sarvam TTS API
  │            │  │  (Agent Speaks Back)     │
  │  4 Screens:│  │          │               │
  │  Session   │  │          ▼               │
  │  Chat      │  │  Outbound Calls          │ ← Twilio SDK
  │  Record    │  │  (Automated Follow-Ups)  │
  │  Dashboard │  │          │               │
  │            │  │          ▼               │
  │  React 18  │  │  Customer Simulation     │
  │  TypeScript│  │  (4 Personas for Testing)│
  │  Tailwind  │  └──────────────────────────┘
  └────────────┘
```

---

## 48-HOUR SPRINT SCHEDULE

> Times are from the start of the hackathon (Hour 0 = Day 1, 9:00 AM).

| Time Block | What Happens | Who |
|---|---|---|
| **Hour 0–1** | Shaurya sets up GitHub repo, pushes prerequisites, invites teammates. Everyone clones the repo and installs dependencies. All API keys obtained and tested. | All |
| **Hour 1–8** | Task 1A: ASR pipeline working. Task 2A: NLP pipeline working. Task 3: Session Start screen built. Task 4A: TTS working. | Parallel work |
| **Hour 8–16** | Task 1B: Dialogue Agent with Redis memory working for both domains. Task 2B: FastAPI server up with all endpoints returning test data. Task 3: Chat screen with WebSocket connected. Task 4B: Twilio outbound call making a real test call. | Parallel work |
| **Hour 16–20** | Task 1C: RLAIF Reward Engine producing scored output. Task 2C: Database saving sessions and turns. Task 3: Record Viewer screen working with mock data. | Parallel work |
| **Hour 20–24** | **First integration checkpoint.** Shaurya reviews and merges Task 2 PR. Backend + AI Core connected. End-to-end text conversation working via API. | Shaurya leads |
| **Hour 24–32** | Task 3: Dashboard screen + live API connection for all screens. Task 4C: Simulation running and printing scored results. Integration of Task 3 frontend with live backend data. | Nayaj + Mouriyan |
| **Hour 32–36** | **Second integration checkpoint.** Merge Task 3 and Task 4 PRs. Full end-to-end demo: browser → chat → record → score. | Shaurya leads |
| **Hour 36–40** | Full pipeline testing with all 4 simulated personas. Bug fixing. UI polish. | All |
| **Hour 40–44** | Demo rehearsal. Presentation preparation. Update PPT with live screenshots. | All |
| **Hour 44–48** | Final submission. Buffer time for last-minute fixes. | All |

---

## WHAT THE DEMO WILL SHOW (Practice This 5 Times)

1. Open browser → `http://localhost:3000`
2. Select **"Healthcare"** domain → Click **"Start Conversation"**
3. Type: *"Main Ramesh hoon, mujhe teen din se bukhar hai"* → Send
4. The agent replies in Hindi. Sentiment bar turns yellow. "symptoms" and "duration" tick green in the Entity Panel.
5. Continue 4 more turns. All required fields fill up. **"View Record"** button appears.
6. Click **"View Record"** → see the full structured healthcare record.
7. Edit one field to show human-in-the-loop validation.
8. Click **"Score Conversation"** → Score Card appears with LLM judge ratings.
9. Switch to terminal → run simulation → show multi-persona automated testing with reward scores.
10. Switch to Dashboard → show historical sessions, search by patient name.

**This 10-step demo covers every single requirement in the PDF.**

---

## KEY RESEARCH REFERENCES
> Cite these when presenting. They are real, peer-reviewed papers.

| Paper / Resource | What It Powers |
|---|---|
| **IndicVoices** — Javed et al., ACL 2024 — 12,000 hours of Indian speech from 22 languages | ASR model training backbone |
| **IndicVoices-R** — Sankar et al., NeurIPS 2024 — 1,704 hours of TTS data, 10,496 speakers | TTS model quality benchmark |
| **Sarvam-M** — Sarvam AI, 2025 — Mistral-Small fine-tuned with SFT + RLVR, +20% Indic benchmarks | Primary dialogue agent |
| **RLAIF vs. RLHF** — Lee et al., Google Brain, 2023 — AI feedback achieves same quality as human feedback | Our self-improving reward loop |
| **Indic-Parler-TTS** — AI4Bharat × HuggingFace, 2024 — 18 Indian languages, Apache 2.0 licence | Voice synthesis |
| **XLM-RoBERTa on SentiMix** — ScienceDirect 2024 — F1-score of 84.8% on Hinglish sentiment | Code-mixed sentiment classifier |
| **IndicLID + IndicXlit** — AI4Bharat — language identification and Romanized script transliteration | Code-mixed text normalization |
| **DPO** — Rafailov et al., Stanford, 2024 — direct preference optimization without a reward model | Future fine-tuning pipeline |

---

## CONTINGENCY PLAN (When Things Break at 2AM)

| Problem | Quick Fix |
|---|---|
| Sarvam API key not approved yet | Use `transcribe_local()` with IndicWhisper — add 3–5 seconds latency but fully works offline |
| No GPU on the laptop | Set `device=-1` in all HuggingFace pipeline calls — uses CPU, slower but functional |
| Frontend WebSocket not connecting | Demo using the FastAPI auto-docs at `http://localhost:8000/docs` — call endpoints manually |
| Twilio call not working | Show the simulation script output in the terminal instead — same pipeline, no actual phone call |
| Database not starting | Use SQLite as a fallback — one-line change in `database.py`, no Docker needed |
| Merge conflict on GitHub | Do not try to resolve it yourself — message Shaurya immediately, share your screen |
| LLM judge API too slow | Pre-generate 3 scored conversation examples and paste them into a JSON file to display in the demo |

---

*Team AGNISHAKTI | SRMIST Chennai | Hack2Future 2.0*
*Research Foundation: AI4Bharat (IIT Madras) · Sarvam AI · Google Brain · HuggingFace*

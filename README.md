# AI Debate Judge

**A local-first, explainable AI system for structured evaluation of written debates.**

AI Debate Judge is a B.Tech Computer Engineering (AI & ML) minor project at Silver Oak University / Silver Oak College of Engineering & Technology. It evaluates **argumentative performance within a supplied debate transcript** and aims to produce a structured, traceable judgment.

> **Boundary:** The system evaluates arguments available in the transcript. It is not an independent fact-checker, does not establish objective truth, and is not validated for high-stakes decision-making.

## Contents

- [Overview](#overview)
- [V1 scope](#v1-scope)
- [Judging workflow](#judging-workflow)
- [Scoring rubric](#scoring-rubric)
- [Architecture and stack](#architecture-and-stack)
- [Repository layout](#repository-layout)
- [Setup](#setup)
- [Run](#run)
- [Tests](#tests)
- [API](#api)
- [Model configuration](#model-configuration)
- [Security and data](#security-and-data)
- [Research and evaluation](#research-and-evaluation)
- [Limitations and deferred scope](#limitations-and-deferred-scope)
- [Development status](#development-status)
- [Project history](#project-history)
- [License](#license)

## Overview

Human evaluation of debates requires more than counting arguments or comparing scores. A useful judge should identify claims, examine reasoning, recognize responses to opposing arguments, assess which issues matter most, and explain its decision.

The project explores whether structured computational argument analysis and explicit adjudication can make the evaluation of written debates more consistent, inspectable and explainable.

**Intended audiences:** students, educators, debate coaches and people seeking structured feedback on written two-sided arguments. These are intended users, not validated deployment claims.

Core principles:

1. Evaluate argumentative performance, not external factual truth.
2. Make findings traceable to the supplied transcript.
3. Keep the verdict distinct from the numerical scorecard.
4. Use one local model in two logical stages for V1.
5. Validate structured outputs and bound model generation.
6. Keep V1 deliberately narrow until it has been properly evaluated.

## V1 scope

| Area | V1 decision |
|---|---|
| Input | One English, two-sided debate transcript |
| Upload formats | TXT, DOCX and PDF |
| Inference | Local Ollama |
| Selected model | `qwen3:8b` |
| Model stages | Two logical stages using the same model |
| Interface | Streamlit |
| Backend | FastAPI |
| Persistence | SQLite |
| Output | Adjudication, deciding issue, scorecard and supporting analysis |

Intended flow:

1. User registers or signs in.
2. User uploads a transcript.
3. The application extracts text.
4. The backend runs the local judging pipeline.
5. The result is displayed and stored in Debate History.

File extraction code exists for TXT, DOCX and PDF. Each format and its edge cases should be tested in the target environment. Text extraction from a PDF does not imply OCR support for scanned pages.

## Judging workflow

**Transcript → Argument extraction → Evidence/source attribution → Rebuttal and clash analysis → Adjudication → Scorecard and explanation**

The broader methodology has also been described as:

**Transcript → Claim extraction → Evidence → Rebuttal matching → Fallacy analysis → Scoring → Explanation**

These describe the intended analytical workflow; they do not imply that every proposed module is a separately implemented or independently validated subsystem.

### Two-stage model workflow

- **Stage 1 — Analysis:** Structure the transcript and identify arguments and relationships.
- **Stage 2 — Adjudication:** Use the structured analysis to produce the judgment and explanation.

Both stages use the same local Ollama model. Python handles orchestration, parsing/validation, consistency checks, persistence and score-related processing. V1 is not a multi-model voting panel.

### Verdict versus score

The winner/status decision and numerical scorecard are separate outputs. A close or tied score must not automatically be presented as a decisive winner. The explanation should identify the deciding issue where the evidence supports one.

## Scoring rubric

| Dimension | Weight |
|---|---:|
| Reasoning | 25% |
| Clash | 20% |
| Weighing | 20% |
| Clarity | 15% |
| Strategy | 10% |
| Persuasion | 10% |
| **Total** | **100%** |

The rubric uses a 1–10 scale.

**Persuasion fairness constraint:** Persuasion may resolve a substantive tie, but must not reward charm, confidence, volume, pace, fluency, accent, dialect, vocabulary or polish.

These are project-defined weights, not a claim that the rubric has been psychometrically validated.

## Architecture and stack

| Layer | Technology | Responsibility |
|---|---|---|
| UI | Streamlit | Authentication, upload, history and results |
| API | FastAPI | Authentication and debate routes |
| Application logic | Python | Transcript processing and judging orchestration |
| Inference | Ollama + Qwen3:8B | Stage 1 analysis and Stage 2 adjudication |
| Database | SQLite + SQLAlchemy | Users, debates and stored results |
| Password hashing | Argon2 | Password hash generation and verification |
| File extraction | `pypdf`, `python-docx`, Python | PDF, DOCX and TXT extraction |
| Validation | Pydantic and project JSON validation | Request and structured-output handling |
| Tests | pytest | Automated regression and unit checks |

```text
                         LOCAL MACHINE
┌────────────────────────────────────────────────────────────┐
│  User                                                      │
│   │                                                        │
│   ▼                                                        │
│  Streamlit UI ── upload / extract transcript               │
│   │                                                        │
│   ▼                                                        │
│  FastAPI backend ───────────────► SQLite database          │
│   │                               users / debates / results│
│   ▼                                                        │
│  Judge pipeline                                            │
│   ├── Stage 1: structured analysis                         │
│   └── Stage 2: adjudication                                │
│             │                                              │
│             ▼                                              │
│       Local Ollama server ──► Qwen3:8B                     │
└────────────────────────────────────────────────────────────┘
```

The current Streamlit interface performs file extraction before submitting transcript text to the API. Moving ingestion behind a dedicated API endpoint has been identified as possible future work, not as current behavior.

## Repository layout

High-level guide; consult the actual checkout for the authoritative complete tree.

```text
AI_Debate_Judge/
├── app/
│   ├── api/routes/
│   ├── db/
│   ├── llm/
│   ├── schemas/
│   ├── security/
│   └── services/
│       ├── file_ingestion.py
│       └── judge_pipeline.py
├── configs/
│   ├── model_config.json
│   └── rubric_v1.json
├── docs/
├── prompts/
├── tests/
├── ui/
│   └── streamlit_app.py
├── requirements.txt
└── README.md
```

Key files:

| File | Purpose |
|---|---|
| `app/main.py` | FastAPI entry point and router registration |
| `app/services/judge_pipeline.py` | Main analysis and adjudication orchestration |
| `app/services/file_ingestion.py` | TXT, DOCX and PDF text extraction |
| `app/llm/ollama_client.py` | Ollama request handling |
| `app/llm/json_validator.py` | Structured JSON parsing/validation helpers |
| `ui/streamlit_app.py` | Streamlit interface |
| `configs/model_config.json` | Model and generation settings |
| `configs/rubric_v1.json` | Rubric weights and persuasion constraint |
| `requirements.txt` | Python dependencies |
| `tests/` | Automated tests |

The main judging pipeline is intentionally kept in `app/services/judge_pipeline.py`; it was not split during the repository cleanup.

## Setup

Requirements: Python 3.11 is the reported development environment; Ollama must be installed and running locally; the selected `qwen3:8b` model must be available. V1 uses local inference and does not require a paid online LLM API.

### 1. Pull the model

```powershell
ollama pull qwen3:8b
ollama list
```

Confirm `qwen3:8b` appears.

### 2. Open the repository

```powershell
cd "path\to\AI_Debate_Judge"
```

### 3. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation scripts, invoke the environment's Python directly rather than changing the machine-wide execution policy.

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

Start the API in one terminal:

```powershell
uvicorn app.main:app --reload --port 8000
```

Start Streamlit in a second terminal, from the repository root:

```powershell
streamlit run ui/streamlit_app.py
```

Open the local Streamlit URL printed in the terminal (normally `http://localhost:8501`).

Health endpoint:

```text
http://127.0.0.1:8000/health
```

Alternatively, use the virtual-environment interpreter explicitly:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
.\.venv\Scripts\python.exe -m streamlit run ui/streamlit_app.py
```

## Tests

Run from the repository root:

```powershell
python -m pytest -q
```

Or without activating the environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The repository cleanup session recorded **16 tests passing**. Re-run the suite on the current checkout to confirm its present state. This automated result does not prove live Ollama inference, end-to-end acceptance, or correctness of every debate judgment.

Optional syntax compilation check:

```powershell
python -m compileall -q app tests
```

Automated tests can verify isolated code paths, parsing and request construction. They do not establish that Ollama is running, that the model is installed, that all file formats work for all documents, that every upload-to-verdict run succeeds, or that judgments agree with expert human adjudicators.

## API

The current FastAPI application registers authentication and debate routes.

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/register` | Register a user |
| `POST` | `/login` | Authenticate a user |
| `GET` | `/debates` | Retrieve the authenticated user's debate history |
| `GET` | `/debates/{debate_id}` | Retrieve a debate and stored result |
| `POST` | `/debates` | Submit a debate for analysis |
| `DELETE` | `/debates/{debate_id}` | Delete a debate belonging to the authenticated user |
| `GET` | `/health` | API health check |

For exact request/response contracts, consult the route modules and schemas under `app/`.

## Model configuration

The current configuration inspected during the documentation cleanup was:

```json
{
  "provider": "ollama",
  "base_url": "http://127.0.0.1:11434",
  "model": "qwen3:8b",
  "temperature": 0.0,
  "timeout_seconds": 180,
  "disable_thinking": true,
  "num_ctx": 8192,
  "stage1_chunk_chars": 4000,
  "stage1_chunk_num_predict": 2048,
  "stage1_structure_num_predict": 1536,
  "stage2_num_predict": 2048
}
```

These values are configuration settings, not guarantees of runtime or output quality. Keep this section aligned with `configs/model_config.json`; do not copy stale values from older handoffs over the current file without inspecting it.

The Ollama client requests JSON output, disables Qwen3 thinking for structured-output stages, and applies bounded output-token budgets. These safeguards reduce some failure modes but cannot guarantee valid or complete output for every transcript.

## Security and data

Security-related implementation observed in the current codebase:

- Passwords are hashed using Argon2 through `argon2-cffi`.
- Debate queries are scoped by user identity in the relevant API routes.
- Transcript content is treated as untrusted model input.
- The V1 flow does not call an online LLM provider.

**Security qualification:** The current authentication flow returns a user ID and uses that identity in request handling. Replacing header-based user ID transport with signed, secure session cookies has been identified as future work. Do not describe the current implementation as a fully hardened session-management system.

This is an academic prototype, not a security-audited production service. Avoid submitting confidential or personally identifying debate material unless the data-handling implications have been assessed.

## Research and evaluation

The research question concerns whether structured argument analysis and explicit adjudication can produce useful, explainable judgments of argumentative performance. A working application or passing unit tests alone does not establish research validity, novelty, accuracy or agreement with human judges.

### IBM Debate Speeches: annotation interpretation

The project investigated IBM Debate Speeches as an evaluation resource. The inspected data was reported to contain 948 rows, including 946 non-empty transcripts, with fields including:

- `topic_id`
- `topic`
- `source`
- `text`
- `goodopeningspeech`
- `mostargumentssupport`
- `interestingspeaker`
- `#labelers`
- `motion_set`

**Critical limitation:** these are speech-level annotations about opening-speech qualities. They are not labels for the six V1 rubric dimensions and are not debate-winner labels. The resource does not provide paired, complete two-sided debates for ordinary winner-accuracy evaluation.

Therefore:

- Selected AI speech-analysis observations may be compared with relevant human feedback if the relationship is explicitly defined.
- Do not present IBM annotations as gold-standard labels for Reasoning, Clash, Weighing, Clarity, Strategy or Persuasion.
- Do not calculate full debate-winner accuracy from these annotations.
- Do not turn a single opening speech into an apparent two-sided debate by inventing an opposing side.
- Disclose any adaptation required to run a speech through the two-sided application.

An exploratory run described in the project history exposed problems when a single-speaker opening speech was represented as a two-sided debate, including unsupported opposing-side output and an invalid two-sided judgment. This is a warning about input suitability and evaluation design, not a benchmark result.

### Evaluation reporting

For each experiment, preserve:

1. Exact dataset record identifier and source transcript.
2. Unmodified input supplied to the application.
3. Model name and relevant configuration.
4. Complete model/application output.
5. Runtime and error information.
6. Exact human annotation being compared.
7. Comparison method and limitations.

Never manufacture labels, scores, winners, ground truth or accuracy figures. Separate observations from interpretations and hypotheses.

## Limitations and deferred scope

Known limitations:

- No independent external fact-checking.
- V1 targets English, written, two-sided debate transcripts.
- OCR for scanned PDFs is not established as supported.
- Model output may be incomplete, malformed or inconsistent despite structured-output safeguards.
- Runtime and output quality depend on hardware, model build, input length and generation settings.
- The project-defined rubric still requires evaluation for validity and reliability.
- IBM Debate Speeches is not a full debate-winner benchmark.
- Authentication/session handling is not production-hardened.
- Passing automated tests is not equivalent to live-model or end-to-end evaluation.

V1 decisions:

| Topic | Decision |
|---|---|
| Multiple model/judge panel | Not part of V1 |
| Online/cloud LLM API | Not part of V1; local Ollama selected |
| External fact-checking | Not a winner criterion |
| Live audio/video judging | Out of scope |
| Training a large model from scratch | Not planned |
| AI Debater that generates arguments | Deferred |
| Vāda/Jalpa/Vitandā and Anekāntavāda/Syādvāda | Deferred pending scholarly operationalization and evaluation |
| Domestic-conflict mediator | Separate future concept, not V1 |
| PostgreSQL deployment profile | Future consideration after local SQLite is stable |

Do not expand the scope during routine maintenance unless the project owner explicitly changes it.

## Development status

This table separates code presence from verified behavior.

| Area | Status |
|---|---|
| Streamlit interface | Present in repository |
| FastAPI application and routes | Present in repository |
| SQLite persistence | Present in repository |
| Argon2 password hashing | Present in repository |
| Ollama client and Qwen3:8B configuration | Present in repository |
| Two-stage judging pipeline | Present in repository |
| TXT/DOCX/PDF extraction code | Present; format-specific behavior should be tested |
| Structured JSON handling and bounded generation | Implemented in repository |
| Automated pytest suite | 16 tests passed in recorded cleanup session; rerun on current checkout |
| Live Ollama inference | Not established by the 16-test result |
| Full end-to-end acceptance across representative debates | Not established by the 16-test result |
| Agreement with expert human judges | Not established |
| Production security audit | Not performed |

## License

No license file is currently documented here. Until a license is deliberately selected and added to the repository, do not assume that the project is released under an open-source license or that reuse is permitted.

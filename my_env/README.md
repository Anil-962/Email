# 🚀 OmniTask AI - Autonomous Inbox & Workflow Engine

## 🎯 Problem Statement
Modern professionals lose roughly 28% of their work week managing email inboxes and attempting to triage isolated tasking systems. Traditional interfaces are completely static, demanding tedious manual extraction, sorting, and context-switching. OmniTask AI seeks to eliminate this massive friction point by marrying secure Google OAuth inbox parsing natively with proactive Agentic AI tooling and True "Edge" NLP processing. The end result is an intelligent dashboard capable of autonomously intercepting, ranking, routing, and fundamentally executing corporate workloads automatically. 

## ✨ Core Features
- **📩 Native Gmail Interception (Two-Way)**: Directly syncs end-user inboxes strictly using localized, highly-secure OAuth2 desktop flows. Automatically maps complex email thread payloads into localized standard task queues, while retaining capabilities to autonomously broadcast programmatic responses securely outbound without ever exposing plain-text credentials.
- **⚡ True Edge NLP Triage**: Completely avoids unnecessary API charges using an embedded HuggingFace `distilbert` zero-shot classification pipeline. The platform scores language semantics dynamically across local system environments to triage `high`, `medium`, or `low` priority entirely offline.
- **🧠 Agentic Operations Engine**: Does not stop at sorting; it executes. The application maps OpenAI GPT structures securely inside strict Pydantic JSON parameters forcing it to use Function Calling. The Agent autonomously triggers workflows, synthesizes deliverables, drafts replies, executes the operation, updates the localized SQLAlchemy SQLite backend, and marks tasks complete autonomously.
- **🌊 SSE Context Streaming**: Frontend client environments dynamically link directly into backend evaluation loops securely via Server-Sent Events (SSE). Core logic inferences instantly stream out byte-by-byte into a polished, terminal-like GUI mimicking live hacker logs elegantly.
- **🛡️ Enterprise Fault Protection**: Centralizes system telemetry via an explicit, production-grade logger hook. Outbound crashes instantly map gracefully against global exception handlers averting unhandled stack trace leaks for absolute hackathon-level professionalism.

## 🛠 Tech Stack
### Backend Environment (Clean Architecture):
- **FastAPI / Uvicorn**: High-performance HTTP/Websockets framework maintaining explicit decoupling.
- **SQLAlchemy & SQLite**: Built on rigorous Object Relational Mapping (ORM) allowing single-click database scaffolding instantly upgradeable to AWS Postgres deployments. 
- **Google Client Libraries**: Validates remote mapping directly onto native Google Cloud APIs utilizing explicit `.readonly` and `.send` scopes independently.
- **PyTorch/Transformers**: Offline deterministic heuristic logic matrices.

### Frontend Environment:
- **Vite & React**: Lightning-fast isolated front-end generation.
- **Tailwind CSS**: Rapid structural deployment building absolutely strictly spaced, pristine UI aesthetics.
- **Framer Motion**: Hardware-accelerated fluid state-cycle transitions natively reorganizing grid priorities safely visually.

## ⚙️ How It Works (The Execution Loop)

1. **Authentication Verification (`gmail_service.py`)**: End-users authorize explicitly bounded logic protocols resulting in localized JSON security tokens ensuring no hardcoded variables reach repository level.
2. **Inlet Data Operations (`main.py`)**: The user imports the Inbox and adds new data to local logic chains. Broad dependencies filter down to `nlp.py` assessing dynamic context to route severity metrics immediately dynamically into database architectures via Dependency Injection.
3. **Execution Routing (`ai_engine.py`)**: End-users actively invoke `/run-ai-stream`. The LLM scans the pending Database elements directly via SQLAlchemy. It assesses priority and commands the bound `process_task` tool, completing workflows and mapping artifacts back into the data grid concurrently natively yielding logic outputs to standard endpoints.
4. **Resolution Layout (`App.jsx`)**: The front-end renders all artifacts cohesively. Email threads automatically synthesize logic via the `/generate-reply` endpoints returning `informal` or `formal` payloads mapping elegantly visually.

---

### 🚀 Local Deployment Setup

**1. Secure Remote Dependencies:**
Ensure your local backend has keys mounted natively.
```bash
export OPENAI_API_KEY="sk-xxx"
```
Place your authorized Google Cloud `credentials.json` directly inside `./server`.

**2. Synchronize Package Structure:**
```bash
# Navigate to API
cd ./server

# Trigger massive environment sync
uv add fastapi uvicorn pydantic openai sqlalchemy transformers torch google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Run backend deployment
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**3. Mount Client Structure:**
```bash
# Navigate to Client environment
cd ./client

npm install
npm run dev
```

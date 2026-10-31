# 🛡️ Safe CSV Analyst & Self-Healing AI Code Execution Agent
**Team:** ALGOTITANS  
**Submission Category:** Autonomous AI Agents / Reliable AI Systems / Data Analytics  

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15+-black?logo=next.js&logoColor=white)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Pytest-19%2F19%20Passing-brightgreen?logo=pytest)](https://pytest.org)
[![Security](https://img.shields.io/badge/Sandbox-AST%20Validated-blue)](#security--sandbox-model)

---

## 💡 Executive Summary

Traditional "AI for CSV" tools either fabricate numerical answers or execute unverified, unsafe code that can compromise server environments or crash at the first syntax error or KeyError.

**Safe CSV Analyst** solves both problems:
1. **Never Hallucinates Computations:** Natural language questions are converted into real Python/Pandas code that runs on actual data.
2. **Self-Healing AI Code Execution:** When code encounters runtime errors (e.g. column casing issues, date formatting, or division by zero), our autonomous diagnostic agent captures the traceback, pinpoints the root cause against the dataset schema, generates corrected code, and recovers execution within a limited retry budget.
3. **Hardened Sandbox Isolation:** Code is strictly pre-screened with an AST Security Visitor and executed in an isolated subprocess worker with stripped credentials, hard execution timeouts, and memory constraints.

---

## 🌟 Key Differentiating Features

- **🔄 Self-Healing Execution Agent:** Up to 2 automatic repair loops per query with visible step-by-step diagnostic and recovery timeline.
- **🛡️ Multi-Layer Security Architecture:**
  - AST Static Analysis disallowing dangerous libraries (`os`, `sys`, `subprocess`, `requests`, `eval`, `open`, etc.).
  - Child process worker isolation that never exposes API keys or host environment variables.
  - Hard timeouts preventing CPU starvation or infinite loops.
- **📊 Interactive Visualizations:** Automatically renders Bar, Line, Pie, Area, and Scatter charts with Recharts, accompanying result tables and statistics.
- **🔌 Provider-Independent AI Layer:** Modular LLM abstraction supporting **Google Gemini** (`gemini-2.0-flash`), **OpenAI-Compatible** (`gpt-4o-mini`, Groq, Ollama), and a **Deterministic Mock Provider** for zero-cost offline hackathon evaluation.
- **📂 Industrial-Grade CSV Processing:** Automatic delimiter sniffing (comma, semicolon, tab, pipe), encoding detection, missing value analysis, duplicate row tracking, and descriptive column metrics.

---

## 🏗️ Architecture

```
User Query ──► AST Validator ──► Isolated Sandbox ──► [Success] ──► Verified Chart & Insights
                                       │
                                   [Failure]
                                       │
                                       ▼
                       AI Self-Healing Diagnostic Agent
                                       │
                                       ▼
                         Corrected Code & Retry Loop
```

*See [ARCHITECTURE.md](./ARCHITECTURE.md) for full technical breakdown and dataflow diagrams.*

---

## 🚀 Quick Start Guide

### Option 1: Run Locally

#### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Run automated tests
pytest tests/ -v

# Start FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend API available at `http://localhost:8000` (Swagger docs at `/docs`)*

#### 2. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
*Application available at `http://localhost:3000`*

---

### Option 2: Docker Compose
```bash
docker compose up --build
```

---

## 🎬 Hackathon Live Demo

*Follow our comprehensive [DEMO_GUIDE.md](./DEMO_GUIDE.md) to experience the live self-healing recovery workflow and pre-loaded sample datasets.*

---

## 🧪 Automated Test Suite (19 / 19 Passing)

The project includes thorough automated test coverage:
- `test_code_validator.py`: Blocks dangerous modules, forbidden calls, dunder exploitation, and syntax errors.
- `test_csv_service.py`: Tests CSV loading, delimiter detection, metadata extraction, and column statistics.
- `test_execution_sandbox.py`: Tests clean execution, KeyError capture, security policy blocks, and execution timeouts.
- `test_self_healing.py`: End-to-end self-healing recovery workflow test verifying failure detection, AI diagnosis, code repair, and recovery.
- `test_api.py`: Tests health checks, dataset uploading, sample loading, and settings management.

Run tests anytime with:
```bash
cd backend && ./venv/bin/pytest tests/ -v
```

---

## 👥 Built by Team ALGOTITANS
*Lablab.ai Hackathon Submission — Autonomous Data Science with Zero Trust Execution.*

# 🛡️ Safe CSV Analyst & Self-Healing AI Code Execution Agent
**Team:** ALGOTITANS  
**Submission Category:** Autonomous AI Agents / Reliable AI Systems / Data Analytics  

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15+-black?logo=next.js&logoColor=white)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Pytest-33%2F33%20Passing-brightgreen?logo=pytest)](https://pytest.org)
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

## 🌐 Production Cloud Deployment Guide

Safe CSV Analyst is architected for seamless separation between static frontend edge hosting (e.g. **Vercel**) and Python ASGI backend execution (e.g. **Render**).

### 1. Backend Deployment (Render)

1. **Create a New Web Service** on [Render](https://render.com) connected to this repository (`ALGO-TITANS/lablab-first-hackathon`).
2. Configure settings:
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Configure Environment Variables in Render:
   | Key | Recommended Value | Note |
   |-----|-------------------|------|
   | `ENVIRONMENT` | `production` | Automatically disables debug endpoints |
   | `DEBUG` | `False` | Disables debug mode |
   | `CORS_ORIGINS` | `https://your-frontend.vercel.app` | Comma-separated list of allowed origins (no `*`) |
   | `DEFAULT_LLM_PROVIDER` | `mock` (or `gemini` / `openai`) | Set API keys if using `gemini` or `openai` |
   | `GEMINI_API_KEY` | *(optional)* | Your Google Gemini API Key |
   | `OPENAI_API_KEY` | *(optional)* | Your OpenAI / Groq API Key |

#### ⚠️ Render Persistent Storage & Ephemeral Filesystem
Render web services run on an **ephemeral disk**. On free or standard restartable instances, uploaded CSV files in `data/uploads` and the SQLite database (`metadata.db`) are wiped whenever the service restarts, deploys, or sleeps.
- **For Permanent Data on Render:** Add a **Persistent Disk** in the service settings:
  - **Mount Path:** `/var/data`
  - **Environment Variable:** `DATA_DIR=/var/data`
  - The backend dynamically places all uploads (`/var/data/uploads`) and SQLite records (`/var/data/metadata.db`) on this persistent volume.
- **Enterprise Multi-Instance Note:** For horizontal auto-scaling across multiple containers, replace SQLite with a managed PostgreSQL instance and store uploaded datasets in AWS S3 or Google Cloud Storage.

---

### 2. Frontend Deployment (Vercel)

1. **Import Project** on [Vercel](https://vercel.com) from GitHub (`ALGO-TITANS/lablab-first-hackathon`).
2. Configure settings:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** `frontend`
3. Configure Build Environment Variable:
   | Key | Value | Security Note |
   |-----|-------|---------------|
   | `NEXT_PUBLIC_API_URL` | `https://your-backend-app.onrender.com` | Publicly exposed to client browsers |

> [!WARNING]
> **Client-Side Environment Security Notice:**
> In Next.js, all environment variables prefixed with `NEXT_PUBLIC_` are inlined directly into browser JavaScript bundles at build time. They are completely visible in browser DevTools and network requests. **Never put API secrets, database passwords, or private LLM keys in `NEXT_PUBLIC_*` variables.** All LLM keys and database operations remain strictly on the backend.

---

## 🔒 Security Audit & Sandbox Boundary Analysis

Safe CSV Analyst applies a rigorous defense-in-depth model:
1. **AST Static Code Analysis:** Rejects prohibited modules (`os`, `sys`, `subprocess`, `socket`, `builtins`, `pickle`, `ctypes`, etc.) and dangerous calls (`eval`, `exec`, `open`, `globals`, `__subclasses__`).
2. **Subprocess Isolation:** Executes in a detached worker process with an emptied environment dictionary so credentials (`GEMINI_API_KEY`, `OPENAI_API_KEY`) cannot be read.
3. **Execution Limits:** Hard wall-clock timeouts (8.0s) and memory caps prevent infinite loops and runaway tasks.

### ⚠️ Multi-Tenant Boundary Disclaimer
> [!CAUTION]
> **Subprocess & AST Isolation is NOT a Multi-Tenant Security Boundary.**
> While the AST validator and subprocess isolation protect against accidental malicious code and credential exposure in development, single-tenant, or controlled hackathon environments, Python AST analysis cannot guarantee containment against kernel zero-days, resource exhaustion (CPU starvation, thread exhaustion), or OS-level side channels when running on a shared host.
>
> **Production Multi-Tenant Recommendation:**
> For hosting untrusted public multi-tenant user code at scale, execution should be delegated to hardware-isolated ephemeral environments:
> - **MicroVM Sandboxes:** AWS Firecracker (via Fly.io Machines, Modal, or Cloudflare Workflows)
> - **Dedicated Sandboxing Services:** E2B, Daytona, or Modal Python sandboxes
> - **Container Sandboxes:** gVisor (`runsc`) with read-only root filesystems, unprivileged user namespaces, and strict cgroups v2 memory/pids throttling.

---

## 🎬 Hackathon Live Demo

*Follow our comprehensive [DEMO_GUIDE.md](./DEMO_GUIDE.md) to experience the live self-healing recovery workflow and pre-loaded sample datasets.*

---

## 🧪 Automated Test Suite (33 / 33 Passing)

The project includes complete automated test coverage:
- `test_code_validator.py`: Blocks dangerous modules, forbidden calls, dunder exploitation, arbitrary file reads/writes, and syntax errors.
- `test_csv_service.py`: Tests CSV loading, delimiter detection, metadata extraction, and column statistics.
- `test_execution_sandbox.py`: Tests clean execution, KeyError capture, security policy blocks, and execution timeouts.
- `test_self_healing.py`: End-to-end self-healing recovery workflow test verifying failure detection, AI diagnosis, code repair, and recovery.
- `test_api.py`: Tests health checks, dataset uploading, sample loading, settings management, **CORS allow/deny policies, wildcard rejection, production DEBUG toggling, and configurable storage paths**.

Run tests anytime with:
```bash
cd backend && ./venv/bin/pytest tests/ -v
```

---

## 👥 Built by Team ALGOTITANS
*Lablab.ai Hackathon Submission — Autonomous Data Science with Zero Trust Execution.*

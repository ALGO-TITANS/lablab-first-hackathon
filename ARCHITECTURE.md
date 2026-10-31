# System Architecture: Safe CSV Analyst & Self-Healing AI Code Execution Agent

## 1. High-Level Architectural Overview

The **Safe CSV Analyst & Self-Healing AI Execution Agent** is architected to eliminate the dual risks of hallucinations and security breaches in AI data science applications.

```
                              ┌──────────────────────────────────────────┐
                              │            Next.js Frontend              │
                              │    React 19 + TypeScript + Tailwind      │
                              │   Recharts Visualizations + Dark HUD     │
                              └────────────────────┬─────────────────────┘
                                                   │ REST / JSON
                                                   ▼
                              ┌──────────────────────────────────────────┐
                              │             FastAPI Backend              │
                              │       Metadata & API Orchestration       │
                              │       Pydantic Schema Validation         │
                              └──────┬────────────────────────────┬──────┘
                                     │                            │
             ┌───────────────────────┴──────┐              ┌──────┴──────────────────────┐
             ▼                              ▼              ▼                             ▼
   ┌───────────────────┐          ┌───────────────────┐  ┌──────────────────┐  ┌───────────────────┐
   │ CSV Service &     │          │ SQLite / Postgres │  │ LLM Provider     │  │ Self-Healing      │
   │ Data Quality      │          │ Metadata Storage  │  │ Abstraction      │  │ Recovery Engine   │
   │ (Encoding/Schema) │          │ (Analyses/Audits) │  │ (Gemini/OpenAI)  │  │ (Max 2 Retries)   │
   └───────────────────┘          └───────────────────┘  └────────┬─────────┘  └────────┬──────────┘
                                                                  │                     │
                                                                  ▼                     │
                                                      ┌───────────────────────┐         │
                                                      │ AST Code Validator    │         │
                                                      │ Forbidden Call Reject │         │
                                                      └───────────┬───────────┘         │
                                                                  │ Validated           │
                                                                  ▼                     │
                                                      ┌───────────────────────┐         │
                                                      │ Isolated Execution    │◄────────┘ (If error)
                                                      │ Worker (Subprocess)   │
                                                      │ Zero Secret Leakage   │
                                                      │ Hard Timeouts (8s)    │
                                                      └───────────────────────┘
```

---

## 2. Core Subsystems

### A. AI Provider Abstraction (`BaseLLMProvider`)
- Enables runtime provider switching without modifying application code.
- Supported drivers:
  1. **Google Gemini (`GeminiLLMProvider`):** Powered by `google-genai` (default `gemini-2.0-flash`).
  2. **OpenAI-Compatible (`OpenAICompatibleLLMProvider`):** Compatible with OpenAI, Groq, Ollama, and local vLLM instances.
  3. **Deterministic Mock (`MockLLMProvider`):** Offline high-reliability provider for zero-API-key evaluation, deterministic testing, and hackathon stage demos.

### B. AST Code Validator (`CodeValidator`)
- Static analysis inspects Python Abstract Syntax Trees prior to execution.
- Disallowed modules: `os`, `sys`, `subprocess`, `shutil`, `socket`, `pty`, `commands`, `builtins`, `importlib`, `pickle`, `ctypes`, `threading`, `urllib`, `requests`, `http`, `ftplib`.
- Disallowed calls: `eval`, `exec`, `compile`, `open`, `__import__`, `globals`, `locals`, `vars`, `breakpoint`, `getattr`, `setattr`.
- Disallowed attributes: `__subclasses__`, `__bases__`, `__globals__`, `__code__`, `__class__`.
- Whitelisted modules: `pandas`, `pd`, `numpy`, `np`, `math`, `datetime`, `json`, `re`, `collections`, `itertools`, `scipy`.

### C. Isolated Execution Sandbox (`ExecutionSandbox` & `sandbox_worker.py`)
- User-generated code is **NEVER** executed inside the main FastAPI application process.
- Execution happens inside an isolated subprocess (`sandbox_worker.py`).
- **Environment Isolation:** Strips all process environment variables (`GEMINI_API_KEY`, `OPENAI_API_KEY`, and system credentials are never forwarded).
- **Execution Limits:** Strict hard timeouts (default: 8.0 seconds), output size truncation, and temporary directory containment.

### D. Self-Healing Execution Orchestrator
When an execution fails (e.g., casing mismatch, type error, date parsing error):
1. Captures the exception type, exact line error, and sanitized traceback.
2. Inquires the LLM repair agent with the failed code, dataset schema, and traceback.
3. Generates a corrected script, re-runs AST validation, and executes attempt #2.
4. Budget: Maximum 2 automatic repair attempts.
5. Populates the complete end-to-end execution timeline in the UI.

---

## 3. Cloud Deployment & Storage Architecture

### A. Frontend Edge Architecture (Vercel)
- The Next.js frontend builds as a static/edge-rendered application communicating with the backend over HTTPS REST.
- `NEXT_PUBLIC_API_URL` configures the backend endpoint.
- **Security Boundary:** All `NEXT_PUBLIC_*` variables are embedded into client-side JS bundles. Zero secrets (API keys, database credentials) are exposed to or handled by the frontend.

### B. Backend Deployment & Persistent Disk Strategy (Render)
- The FastAPI application runs as a stateless Python web service behind an ASGI server (`uvicorn`).
- **Storage Subsystem:**
  - `DATA_DIR` (default: `./data`, configurable via env) controls where dataset files and SQLite metadata reside.
  - On cloud container platforms like Render, the local disk is **ephemeral** by default. Re-deployments and idle tier sleep cycles reset the filesystem.
  - **Single-Node Persistence:** Mount a Render Persistent Disk (e.g., at `/var/data`) and set `DATA_DIR=/var/data`. The application automatically points `uploads/` and `metadata.db` to the mounted volume.
  - **Horizontal Multi-Instance Scaling:** In enterprise production clusters, datasets are streamed to S3-compatible object storage (AWS S3 / Google Cloud Storage) with signed URLs, and metadata is managed via a distributed relational database (PostgreSQL / Supabase).

---

## 4. Security Audit & Sandbox Isolation Evaluation

### Current Protection Layers:
1. **AST Validation:**
   - Static analysis intercepts dangerous Python syntax prior to bytecode compilation or execution.
   - Denies OS manipulation, process invocation, network sockets, reflection (`getattr`, `eval`), and dunder traversal.
2. **Subprocess Credential Sanitization:**
   - Worker scripts execute in a separate process space with an empty environment dictionary (`env={}`).
   - Host environment variables, API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`), and host file descriptors are inaccessible.
3. **Execution Guardrails:**
   - Hard timeout enforcement (`SANDBOX_TIMEOUT_SECONDS = 8.0s`) halts CPU runaway loops.
   - Output truncation limits memory consumption from excessive printing (`SANDBOX_MAX_OUTPUT_CHARS = 200000`).
4. **Public Portfolio Demo Mode & Execution Guard:**
   - In production, `ENABLE_ARBITRARY_EXECUTION` defaults to `False` and `DEMO_MODE` defaults to `True`.
   - Arbitrary subprocess code execution on the host machine is completely blocked for custom CSV uploads.
   - Pre-loaded sample datasets (Global Sales and Customer Churn) run controlled demonstrations with accurate data aggregations.
   - Simulated self-healing workflows demonstrate runtime error detection, LLM diagnosis, code repair, and recovery timelines without running untrusted host subprocesses.
   - Full live subprocess code execution remains active in local development (`ENVIRONMENT="development"`).

### Multi-Tenant Production Security Assessment:
> **Important Security Finding:**
> Python AST parsing and child subprocesses provide strong defense-in-depth for single-tenant, internal tooling, or hackathon review environments. However, they **do not constitute a true multi-tenant virtualization boundary**.
>
> In an adversarial public multi-tenant SaaS environment, determined attackers could theoretically leverage kernel vulnerabilities, cgroup exhaustion, or shared hardware memory attacks to cause denial of service.

### Recommended Multi-Tenant Isolation Architecture:
For public untrusted multi-user deployment:
1. **MicroVM Sandboxes (Gold Standard):**
   - Run each code execution in a dedicated ephemeral MicroVM utilizing **AWS Firecracker** (e.g. Fly.io Machines or Modal).
   - Startup latency: < 150ms with complete kernel-level hardware virtualization.
2. **Kernel-Isolated Container Sandboxes:**
   - Deploy execution workers in **gVisor (`runsc`)** or **Kata Containers**.
   - Intercepts system calls at the application kernel layer without granting raw host kernel access.
3. **Dedicated Cloud Sandbox APIs:**
   - Integrate managed execution runtimes such as **E2B Sandboxes** or **Daytona**, which specialize in isolated code execution for autonomous AI agents.

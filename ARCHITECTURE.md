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

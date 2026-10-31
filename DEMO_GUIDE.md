# 🎬 Hackathon Live Demo Guide: Safe CSV Analyst & Self-Healing AI Agent

This guide outlines the exact demonstration workflow for hackathon judges and evaluators.

---

## ⚡ 60-Second Quick Start

1. **Start the Backend:**
   ```bash
   cd "Lablab.ai Hackathon Submission/backend"
   source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
2. **Start the Frontend:**
   ```bash
   cd "Lablab.ai Hackathon Submission/frontend"
   npm run dev
   ```
3. **Open:** `http://localhost:3000`

---

## 🧭 Step-by-Step Live Walkthrough

### Step 1: Landing Page & Dashboard
- Navigate to `http://localhost:3000`.
- Point out the **dark navy & electric-blue UI**, highlighting the security sandbox badges and self-healing architecture.
- Click **"Launch Platform"** or go to `/dashboard` to view live telemetry: Total Datasets, Queries Executed, Repaired Successes, and Worker Status.

### Step 2: One-Click Sample Dataset Loading or CSV Upload
- Go to `/upload` or click **"Load Global Sales Sample"**.
- Point out the automatic file validation:
  - Delimiter detection (supports comma, semicolon, tab, pipe)
  - Encoding detection (UTF-8, Latin-1, ASCII)
  - Column schema extraction: Data types, missing percentage, unique values, and summary statistics.
- Click into the **Dataset Workspace** to inspect the data preview and summary.

### Step 3: Conversational Analytics Query
- In the analysis chat box, ask:
  > *"What are the top 5 products ranked by total revenue?"*
- Observe the **Execution Timeline**:
  1. `Understanding request`
  2. `Generating Python code`
  3. `Validating code` (AST security check)
  4. `Executing analysis` (Sandboxed worker)
  5. `Verifying results`
  6. `Analysis completed`
- Review the generated interactive **Bar Chart**, formatted data table, and natural language explanation.
- Click **"View Python Code"** to examine the exact Pandas code executed inside the sandbox.

### Step 4: THE DIFFERENTIATING DEMO — Self-Healing Code Recovery
- In the query bar, toggle **"Simulate Runtime Failure (Self-Healing Demo)"** (or use the test button) with the question:
  > *"Show total revenue by region"*
- Watch the live self-healing recovery timeline unfold:
  1. **Attempt #1 Fails:** Initial code attempts `df.groupby('Region')['Revenue']` (mismatched casing).
  2. **Error Detected:** Caught `[KeyError: 'Region']`.
  3. **AI Diagnosis:** The self-healing agent inspects the dataset schema, diagnoses that the column is lowercase `'region'`, and generates repaired Pandas code with column normalization.
  4. **AST Validation:** Repaired script passes security checks.
  5. **Attempt #2 Succeeds:** The sandbox executes the repaired code and outputs verified data.
  6. **Status:** Marked as **REPAIRED (1 Auto-Fix)**.
- Open the **Repair History / Attempt Comparison** to show judges the before-and-after code and the diagnosis explanation!

### Step 5: Security & Isolation Verification
- Try asking to read system files or execute shell commands.
- The **AST Code Validator** immediately blocks prohibited calls (`os.system`, `subprocess.run`, `eval`, `open`) before they can ever execute!

### Step 6: Settings & Multi-Provider Flexibility
- Visit `/settings`.
- Switch between **Mock Provider** (for guaranteed offline demos), **Google Gemini** (`gemini-2.0-flash`), or **OpenAI / Groq** (`gpt-4o-mini`).
- Adjust sandbox timeout thresholds in real-time.

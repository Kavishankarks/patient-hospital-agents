# Patient Hospital Agents

Clinical decision support platform that helps care teams and patients manage
intake, triage, summaries, hospital recommendations, and recovery coaching.
This repository includes a FastAPI backend and a Next.js frontend UI.

## What this project includes

- **Backend (FastAPI)**: Patient records, document/audio ingestion, profiling,
  triage, SBAR summaries, pre-intelligence, hospital recommendations, medication
  plans, recovery coach, and feedback/audit APIs.
- **Frontend (Next.js)**: Role-based UI for patients, doctors, and hospitals to
  view and act on patient data.

## Project structure

- `backend/` — FastAPI application (Python).
- `frontend/` — Next.js application (React).

## Prerequisites

- Python 3.11+
- Node.js 18+

## Run the backend

1. Go to the backend folder:
   ```bash
   cd backend
   ```
2. Install dependencies (uses `uv`):
   ```bash
   uv sync
   ```
3. Start the API server:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. API base URL: `http://localhost:8000`

## Run the frontend

1. Go to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```
4. Open the UI: `http://localhost:3000`

## Configuration

- **Backend uploads directory**: `backend/app/core/config.py` → `UPLOAD_DIR`
- **Frontend API base**: Set in the UI or via `NEXT_PUBLIC_API_BASE`

## Required API keys

Create a `.env` file in `backend/` (or export env vars) with the following:

```bash
OPENAI_API_KEY=your_openai_api_key
```

Optional overrides:

```bash
OPENAI_MODEL_TEXT=gpt-4.1-mini
OPENAI_MODEL_TTS=gpt-4o-mini-tts
OPENAI_MODEL_STT=whisper-1
MCP_HOSPITAL_BASE_URL=http://localhost:9001
```

## Notes

- This tool is for clinical decision support only and does not replace a
  licensed clinician.

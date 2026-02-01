# Patient & Hospital Copilot Backend

## Environment variables
- OPENAI_API_KEY
- OPENAI_MODEL_TEXT
- OPENAI_MODEL_REASONING
- OPENAI_MODEL_TTS
- OPENAI_MODEL_STT
- DATABASE_URL
- REDIS_URL (optional)
- MCP_HOSPITAL_BASE_URL
- UPLOAD_DIR
- NVIDIA_NIM_API_KEY
- NVIDIA_NIM_PAGE_ELEMENTS_URL (optional)

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install fastapi uvicorn[standard] sqlalchemy aiosqlite pydantic pydantic-settings httpx openai pytest
```

## Run
```bash
uvicorn app.main:app --reload --app-dir backend
```

On startup, the app auto-creates tables for hackathon use. For production, wire Alembic migrations.

## Migrations (Alembic)
Create an Alembic setup inside `backend/app/db/migrations` if you want generated revisions.

## API Examples
### Profile
```json
{"conditions": ["hypertension"], "allergies": ["penicillin"], "medications": [{"name": "lisinopril", "dose": "10mg", "frequency": "daily"}], "vitals": {"bp": "140/90"}, "timeline": ["chest tightness x2 days"], "missing_fields": ["smoking_status"]}
```

### Triage
```json
{"level": "AMBER", "red_flags": ["shortness of breath"], "specialty_needed": "cardiology", "safety": ["Decision support only", "Doctor verification required", "Seek emergency help if red flags"]}
```

### SBAR
```json
{"situation": "Chest tightness for 2 days", "background": "HTN on lisinopril", "assessment": "Possible ACS risk; needs evaluation", "recommendation": "Urgent ECG and troponin", "safety": ["Decision support only", "Doctor verification required", "Seek emergency help if red flags"]}
```

### Pre-Intelligence
```json
{"risks": ["ACS risk"], "interactions": ["warfarin + ibuprofen: increased bleeding risk"], "suggested_tests": ["ECG", "troponin"], "differential_hints": ["ACS", "GERD"], "safety": ["Decision support only", "Doctor verification required", "Seek emergency help if red flags"]}
```

### Hospitals
```json
[{"hospital_id": "H1", "name": "City General", "score": 7.2, "why": ["specialty match", "ETA considered"]}]
```

### Medication Plan
```json
{"plan": {"start_date": "2026-01-31", "medications": [{"name": "amoxicillin", "dose": "500mg", "times": ["08:00", "20:00"]}]}}
```

### Daily Coach
```json
{"script_text": "You're doing well today...", "audio_path": "/data/uploads/xyz.mp3"}
```

## Mock MCP Hospital server
Create a small FastAPI app with `/search` and `/capabilities/{hospital_id}` endpoints returning JSON.

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.router import api_router
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
import app.models  # noqa: F401

tags_metadata = [
    {"name": "patients", "description": "Create and fetch patient records."},
    {"name": "ingestion", "description": "Upload documents/audio and extract text."},
    {"name": "profiling", "description": "Build patient profile and triage."},
    {"name": "questionnaire", "description": "Adaptive questions to fill missing info."},
    {"name": "intelligence", "description": "SBAR summaries and pre-intelligence."},
    {"name": "hospitals", "description": "Hospital matching via MCP."},
    {"name": "medications", "description": "Prescriptions and medication tracking."},
    {"name": "coach", "description": "Daily recovery coach scripts and audio."},
    {"name": "feedback", "description": "Doctor feedback and audit views."},
    {"name": "auth", "description": "Login for patients, doctors, and hospitals."},
]

app = FastAPI(
    title='Patient & Hospital Copilot API',
    description=(
        "Clinical decision support tool (not an autonomous prescriber). "
        "Always verify with a licensed clinician."
    ),
    version="0.1.0",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix='/api/v1')

upload_dir = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(upload_dir, exist_ok=True)
app.mount("/data/uploads", StaticFiles(directory=upload_dir), name="uploads")

@app.on_event('startup')
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get('/health')
async def health():
    return {'status': 'ok'}

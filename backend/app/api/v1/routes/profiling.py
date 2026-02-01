from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.models.document import Document
from app.models.transcript import Transcript
from app.models.profile import PatientProfile
from app.models.triage import TriageResult
from app.orchestration.pipeline import build_patient_profile
from app.agents.triage_gate_agent import TriageGateAgent
from app.schemas.triage import TriageOut
from app.utils.safety import ensure_safety
from app.schemas.patient import PatientProfileOut
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post('/{patient_id}/profile/build', response_model=PatientProfileOut)
async def build_profile(patient_id: int, session: AsyncSession = Depends(get_session)):
    """Build a structured patient profile from uploaded docs and transcripts."""
    docs = (await session.execute(select(Document).where(Document.patient_id == patient_id))).scalars().all()
    transcripts = (await session.execute(select(Transcript).where(Transcript.patient_id == patient_id))).scalars().all()
    texts = [d.extracted_text or '' for d in docs] + [t.text for t in transcripts]
    non_empty = [t for t in texts if t and t.strip()]
    input_text = '\\n'.join(non_empty)
    logger.info(
        'profile build input',
        extra={'patient_id': patient_id, 'docs': len(docs), 'transcripts': len(transcripts), 'chunks': len(non_empty), 'chars': len(input_text)},
    )
    if not input_text.strip():
        return PatientProfileOut(
            patient_id=patient_id,
            profile={
                "conditions": [],
                "allergies": [],
                "medications": [],
                "vitals": {},
                "timeline": [],
                "missing_fields": ["no_extracted_text"],
            },
            version=1,
            created_at=None,
        )
    profile, extras = await build_patient_profile(input_text)
    record = PatientProfile(patient_id=patient_id, profile_json=profile, version=1)
    session.add(record)
    triage = extras.get('triage')
    triage_rec = TriageResult(patient_id=patient_id, level=triage['level'], red_flags_json={'red_flags': triage['red_flags']}, specialty_needed=triage.get('specialty_needed'))
    session.add(triage_rec)
    await session.commit()
    await session.refresh(record)
    return PatientProfileOut(
        patient_id=patient_id,
        profile=record.profile_json,
        version=record.version,
        created_at=record.created_at.isoformat() if record.created_at else None,
    )

@router.get('/{patient_id}/profile/latest', response_model=PatientProfileOut)
async def get_latest_profile(patient_id: int, session: AsyncSession = Depends(get_session)):
    """Fetch the latest stored profile for a patient."""
    result = await session.execute(
        select(PatientProfile)
        .where(PatientProfile.patient_id == patient_id)
        .order_by(PatientProfile.created_at.desc())
    )
    record = result.scalars().first()
    if record is None:
        return PatientProfileOut(
            patient_id=patient_id,
            profile={
                "conditions": [],
                "allergies": [],
                "medications": [],
                "vitals": {},
                "timeline": [],
                "missing_fields": ["no_profile"],
            },
            version=0,
            created_at=None,
        )
    return PatientProfileOut(
        patient_id=patient_id,
        profile=record.profile_json,
        version=record.version,
        created_at=record.created_at.isoformat() if record.created_at else None,
    )

@router.post('/{patient_id}/triage', response_model=TriageOut)
async def run_triage(patient_id: int, session: AsyncSession = Depends(get_session)):
    """Run triage (RED/AMBER/GREEN) with red-flag detection and safety footer."""
    docs = (await session.execute(select(Document).where(Document.patient_id == patient_id))).scalars().all()
    transcripts = (await session.execute(select(Transcript).where(Transcript.patient_id == patient_id))).scalars().all()
    texts = [d.extracted_text or '' for d in docs] + [t.text for t in transcripts]
    input_text = '\\n'.join(texts)
    triage = TriageGateAgent().run(input_text)
    triage.safety = ensure_safety(triage.safety)
    return triage

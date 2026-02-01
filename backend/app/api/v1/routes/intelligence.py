from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.intelligence import SBAROut, PreIntelligenceOut, SBARStoredOut
from app.agents.summary_agent import SummaryAgent
from app.agents.preintelligence_agent import PreIntelligenceAgent
from app.services.interaction_rules_service import InteractionRulesService
from app.utils.safety import ensure_safety
from app.db.session import get_session
from app.models.profile import PatientProfile
from app.models.triage import TriageResult
from app.models.document import Document
from app.models.summary import SbarSummary

router = APIRouter()

@router.get('/{patient_id}/summary', response_model=SBAROut)
async def get_summary(patient_id: int, session: AsyncSession = Depends(get_session)):
    """Generate SBAR summary with safety footer."""
    prof = await session.execute(
        select(PatientProfile)
        .where(PatientProfile.patient_id == patient_id)
        .order_by(PatientProfile.created_at.desc())
    )
    profile = prof.scalars().first()
    profile_payload = profile.profile_json if profile else {}
    triage_result = await session.execute(
        select(TriageResult)
        .where(TriageResult.patient_id == patient_id)
        .order_by(TriageResult.created_at.desc())
    )
    triage = triage_result.scalars().first()
    triage_payload = {
        "level": triage.level,
        "red_flags": triage.red_flags_json,
        "specialty_needed": triage.specialty_needed,
    } if triage else {}
    doc_result = await session.execute(
        select(Document)
        .where(Document.patient_id == patient_id)
        .order_by(Document.created_at.desc())
        .limit(3)
    )
    docs = doc_result.scalars().all()
    doc_snippets = [
        (d.extracted_text or "")[:500] for d in docs if d.extracted_text and d.extracted_text.strip()
    ]
    input_text = (
        f"Patient profile JSON:\n{profile_payload}\n\n"
        f"Latest triage:\n{triage_payload}\n\n"
        f"Recent document snippets:\n{doc_snippets}"
    )
    result = SummaryAgent().run(input_text)
    result.safety = ensure_safety(result.safety)
    record = SbarSummary(patient_id=patient_id, sbar_json=result.model_dump())
    session.add(record)
    await session.commit()
    return result


@router.get('/{patient_id}/summary/latest', response_model=SBARStoredOut)
async def get_latest_summary(patient_id: int, session: AsyncSession = Depends(get_session)):
    """Fetch the latest stored SBAR summary."""
    result = await session.execute(
        select(SbarSummary)
        .where(SbarSummary.patient_id == patient_id)
        .order_by(SbarSummary.created_at.desc())
    )
    record = result.scalars().first()
    if record is None:
        return SBARStoredOut(
            patient_id=patient_id,
            sbar=SBAROut(
                situation="",
                background="",
                assessment="",
                recommendation="",
                safety=ensure_safety([]),
            ),
            created_at=None,
        )
    return SBARStoredOut(
        patient_id=patient_id,
        sbar=SBAROut.model_validate(record.sbar_json),
        created_at=record.created_at.isoformat() if record.created_at else None,
    )

@router.get('/{patient_id}/preintelligence', response_model=PreIntelligenceOut)
async def get_preintelligence(patient_id: int, session: AsyncSession = Depends(get_session)):
    """Generate pre-intelligence (risks, interactions, tests) with safety footer."""
    prof = await session.execute(
        select(PatientProfile)
        .where(PatientProfile.patient_id == patient_id)
        .order_by(PatientProfile.created_at.desc())
    )
    profile = prof.scalars().first()
    profile_payload = profile.profile_json if profile else {}
    triage_result = await session.execute(
        select(TriageResult)
        .where(TriageResult.patient_id == patient_id)
        .order_by(TriageResult.created_at.desc())
    )
    triage = triage_result.scalars().first()
    triage_payload = {
        "level": triage.level,
        "red_flags": triage.red_flags_json,
        "specialty_needed": triage.specialty_needed,
    } if triage else {}
    doc_result = await session.execute(
        select(Document)
        .where(Document.patient_id == patient_id)
        .order_by(Document.created_at.desc())
        .limit(3)
    )
    docs = doc_result.scalars().all()
    doc_snippets = [
        (d.extracted_text or "")[:500] for d in docs if d.extracted_text and d.extracted_text.strip()
    ]
    input_text = (
        f"Patient profile JSON:\n{profile_payload}\n\n"
        f"Latest triage:\n{triage_payload}\n\n"
        f"Recent document snippets:\n{doc_snippets}"
    )
    result = PreIntelligenceAgent().run(input_text)
    result.interactions.extend(InteractionRulesService().check([]))
    result.safety = ensure_safety(result.safety)
    return result

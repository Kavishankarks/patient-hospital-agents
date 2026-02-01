from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.schemas.coach import CoachGenerateOut
from app.agents.recovery_coach_agent import RecoveryCoachAgent
from app.services.tts_service import TTSService
from app.utils.safety import safety_footer_text
from app.db.session import get_session
from app.models.coach import CoachMessage, DoctorAdvicePack
from app.models.profile import PatientProfile
from app.models.patient import Patient
from app.models.medication import MedicationPlan, DoseSchedule, DoseLog

router = APIRouter()

@router.post('/{patient_id}/recovery-coach/generate', response_model=CoachGenerateOut)
async def generate_coach(patient_id: int, session: AsyncSession = Depends(get_session)):
    """Generate a daily recovery coach message + TTS audio."""
    result = await session.execute(
        select(PatientProfile)
        .where(PatientProfile.patient_id == patient_id)
        .order_by(PatientProfile.created_at.desc())
    )
    profile = result.scalars().first()
    profile_payload = profile.profile_json if profile else {}
    patient_result = await session.execute(select(Patient).where(Patient.id == patient_id))
    patient = patient_result.scalars().first()
    patient_name = patient.name if patient else "Patient"

    plan_result = await session.execute(
        select(MedicationPlan)
        .where(MedicationPlan.patient_id == patient_id, MedicationPlan.active == True)  # noqa: E712
        .order_by(MedicationPlan.created_at.desc())
    )
    plan = plan_result.scalars().first()
    today = datetime.now(timezone.utc).date().isoformat()
    today_doses: list[dict] = []
    adherence = {"taken": 0, "missed": 0, "skipped": 0}
    if plan:
        dose_result = await session.execute(
            select(DoseSchedule).where(DoseSchedule.plan_id == plan.id, DoseSchedule.due_at.startswith(today))
        )
        doses = dose_result.scalars().all()
        today_doses = [
            {"med_name": d.med_name, "dose": d.dose, "due_at": d.due_at, "status": d.status}
            for d in doses
        ]
        if doses:
            dose_ids = [d.id for d in doses]
            logs = (await session.execute(select(DoseLog).where(DoseLog.dose_id.in_(dose_ids)))).scalars().all()
            for log in logs:
                if log.action == "taken":
                    adherence["taken"] += 1
                elif log.action == "missed":
                    adherence["missed"] += 1
                elif log.action == "skipped":
                    adherence["skipped"] += 1

    advice_result = await session.execute(
        select(DoctorAdvicePack)
        .where(DoctorAdvicePack.patient_id == patient_id)
        .order_by(DoctorAdvicePack.id.desc())
    )
    advice = advice_result.scalars().first()
    advice_payload = advice.advice_json if advice else {}

    input_text = (
        f"Patient name: {patient_name}\\n"
        f"Patient profile JSON:\\n{profile_payload}\\n\\n"
        f"Active medication plan:\\n{plan.plan_json if plan else {}}\\n\\n"
        f"Today's doses:\\n{today_doses}\\n\\n"
        f"Adherence today:\\n{adherence}\\n\\n"
        f"Doctor advice pack:\\n{advice_payload}"
    )
    script = RecoveryCoachAgent().run(input_text)
    script = f"{script}\\n\\nSafety: {safety_footer_text()}"
    audio_path = TTSService().synthesize(script)
    record = CoachMessage(patient_id=patient_id, script_text=script, audio_path=audio_path)
    session.add(record)
    await session.commit()
    return CoachGenerateOut(script_text=script, audio_path=audio_path)

@router.get('/{patient_id}/recovery-coach/latest', response_model=CoachGenerateOut)
async def get_latest(patient_id: int, session: AsyncSession = Depends(get_session)):
    """Return latest coach message."""
    result = await session.execute(
        select(CoachMessage)
        .where(CoachMessage.patient_id == patient_id)
        .order_by(CoachMessage.created_at.desc())
    )
    record = result.scalars().first()
    if record is None:
        return CoachGenerateOut(script_text='', audio_path='')
    return CoachGenerateOut(script_text=record.script_text, audio_path=record.audio_path)

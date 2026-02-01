from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.agents.questionnaire_agent import QuestionnaireAgent
from app.schemas.questionnaire import QuestionnaireNext, QuestionnaireAnswer
from app.db.session import get_session
from app.models.profile import PatientProfile

router = APIRouter()

@router.post('/{patient_id}/questionnaire/next', response_model=QuestionnaireNext)
async def next_questions(patient_id: int, session: AsyncSession = Depends(get_session)):
    """Return next adaptive questions for missing fields."""
    result = await session.execute(
        select(PatientProfile)
        .where(PatientProfile.patient_id == patient_id)
        .order_by(PatientProfile.created_at.desc())
    )
    profile = result.scalars().first()
    profile_payload = profile.profile_json if profile else {}
    input_text = f"Patient profile JSON:\n{profile_payload}"
    return QuestionnaireAgent().run(input_text)

@router.post('/{patient_id}/questionnaire/answer')
async def answer_questions(patient_id: int, payload: QuestionnaireAnswer):
    """Submit questionnaire answers and update profile state."""
    return {'status': 'received', 'answers': payload.answers}

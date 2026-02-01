from fastapi import APIRouter
from app.agents.questionnaire_agent import QuestionnaireAgent
from app.schemas.questionnaire import QuestionnaireNext, QuestionnaireAnswer

router = APIRouter()

@router.post('/{patient_id}/questionnaire/next', response_model=QuestionnaireNext)
async def next_questions(patient_id: int):
    """Return next adaptive questions for missing fields."""
    return QuestionnaireAgent().run('')

@router.post('/{patient_id}/questionnaire/answer')
async def answer_questions(patient_id: int, payload: QuestionnaireAnswer):
    """Submit questionnaire answers and update profile state."""
    return {'status': 'received', 'answers': payload.answers}

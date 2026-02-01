from fastapi import APIRouter
from app.schemas.feedback import FeedbackIn

router = APIRouter()

@router.post('/{patient_id}/feedback')
async def feedback(patient_id: int, payload: FeedbackIn):
    """Submit clinician feedback on summaries or recommendations."""
    return {'status': 'received'}

@router.get('/{patient_id}/audit')
async def audit(patient_id: int, limit: int = 50):
    """Return audit log entries (stub)."""
    return {'items': []}

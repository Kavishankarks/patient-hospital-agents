from fastapi import APIRouter
from app.schemas.prescription import PrescriptionIn, StructuredPrescription
from app.schemas.medication import MedicationPlanIn, DoseLogIn, AdherenceOut
from app.agents.prescription_structurer_agent import PrescriptionStructurerAgent
from app.services.medication_tracker_service import MedicationTrackerService

router = APIRouter()

@router.post('/{patient_id}/prescriptions/structure', response_model=StructuredPrescription)
async def structure_prescription(patient_id: int, payload: PrescriptionIn):
    """Structure doctor prescription text into JSON with clarifications."""
    return PrescriptionStructurerAgent().run(payload.raw_text)

@router.post('/{patient_id}/medication-plans')
async def create_medication_plan(patient_id: int, payload: MedicationPlanIn):
    """Create a medication plan and generate a dose schedule."""
    schedule = MedicationTrackerService().build_schedule(payload.plan, days=1)
    return {'plan': payload.plan, 'schedule': schedule}

@router.get('/{patient_id}/medication-plans/active')
async def get_active_plan(patient_id: int):
    """Fetch the active medication plan (stub)."""
    return {'active': None}

@router.get('/{patient_id}/doses/today')
async def get_doses_today(patient_id: int):
    """Get today's scheduled doses (stub)."""
    return {'doses': []}

@router.post('/{patient_id}/doses/{dose_id}/log')
async def log_dose(patient_id: int, dose_id: int, payload: DoseLogIn):
    """Log a dose as taken/skipped/missed."""
    return {'status': 'logged'}

@router.get('/{patient_id}/adherence', response_model=AdherenceOut)
async def adherence(patient_id: int, days: int = 7):
    """Return adherence stats for the last N days (stub)."""
    return AdherenceOut(taken=0, missed=0, skipped=0)

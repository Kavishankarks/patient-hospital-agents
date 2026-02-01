from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientOut
from app.services.patient_service import create_patient_with_optional_account

router = APIRouter()

@router.get('', response_model=list[PatientOut])
async def list_patients(session: AsyncSession = Depends(get_session)):
    """List all patient records."""
    result = await session.execute(select(Patient).order_by(Patient.id))
    patients = result.scalars().all()
    return [
        PatientOut(
            id=patient.id,
            name=patient.name,
            age=patient.age,
            sex=patient.sex,
            contact_masked=patient.contact_masked,
        )
        for patient in patients
    ]

@router.post('', response_model=PatientOut)
async def create_patient(payload: PatientCreate, session: AsyncSession = Depends(get_session)):
    """Create a patient record. Contact fields are masked before storage."""
    patient, _ = await create_patient_with_optional_account(payload, session)
    return PatientOut(id=patient.id, name=patient.name, age=patient.age, sex=patient.sex, contact_masked=patient.contact_masked)

@router.get('/{patient_id}', response_model=PatientOut)
async def get_patient(patient_id: int, session: AsyncSession = Depends(get_session)):
    """Fetch a patient record by id."""
    result = await session.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one()
    return PatientOut(id=patient.id, name=patient.name, age=patient.age, sex=patient.sex, contact_masked=patient.contact_masked)

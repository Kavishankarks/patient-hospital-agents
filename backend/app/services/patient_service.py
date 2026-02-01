from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.patient import Patient
from app.models.account import Account
from app.schemas.patient import PatientCreate
from app.utils.masking import mask_phi
from app.utils.passwords import hash_password, normalize_mobile

async def create_patient_with_optional_account(
    payload: PatientCreate,
    session: AsyncSession,
) -> tuple[Patient, int | None]:
    if (payload.mobile and not payload.password) or (
        payload.password and not payload.mobile
    ):
        raise HTTPException(
            status_code=400, detail="Mobile and password must be provided together"
        )
    normalized_mobile: str | None = None
    if payload.mobile:
        normalized_mobile = normalize_mobile(payload.mobile)
        existing = await session.execute(
            select(Account).where(
                Account.role == "patient", Account.mobile == normalized_mobile
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(status_code=400, detail="Mobile already registered")
    masked = mask_phi(payload.contact) if payload.contact else None
    patient = Patient(
        name=payload.name,
        age=payload.age,
        sex=payload.sex,
        contact_masked=masked,
    )
    session.add(patient)
    await session.flush()
    account_id: int | None = None
    if normalized_mobile:
        account = Account(
            role="patient",
            mobile=normalized_mobile,
            password_hash=hash_password(payload.password or ""),
            patient_id=patient.id,
        )
        session.add(account)
        await session.flush()
        account_id = account.id
    await session.commit()
    await session.refresh(patient)
    return patient, account_id

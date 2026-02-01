from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.models.account import Account
from app.schemas.auth import LoginRequest, LoginResponse, SignupRequest
from app.schemas.patient import PatientCreate
from app.services.patient_service import create_patient_with_optional_account
from app.utils.passwords import hash_password, normalize_mobile, verify_password

router = APIRouter()

async def _login(role: str, payload: LoginRequest, session: AsyncSession) -> LoginResponse:
    mobile = normalize_mobile(payload.mobile)
    result = await session.execute(
        select(Account).where(Account.role == role, Account.mobile == mobile)
    )
    account = result.scalar_one_or_none()
    if account is None or not verify_password(payload.password, account.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return LoginResponse(role=role, account_id=account.id, patient_id=account.patient_id)

@router.post('/patients/login', response_model=LoginResponse)
async def login_patient(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    return await _login('patient', payload, session)

@router.post('/doctors/login', response_model=LoginResponse)
async def login_doctor(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    return await _login('doctor', payload, session)

@router.post('/hospitals/login', response_model=LoginResponse)
async def login_hospital(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    return await _login('hospital', payload, session)

@router.post('/patients/signup', response_model=LoginResponse)
async def signup_patient(payload: PatientCreate, session: AsyncSession = Depends(get_session)):
    if not payload.mobile or not payload.password:
        raise HTTPException(status_code=400, detail='Mobile and password are required')
    patient, account_id = await create_patient_with_optional_account(payload, session)
    if account_id is None:
        raise HTTPException(status_code=400, detail='Unable to create patient account')
    return LoginResponse(role='patient', account_id=account_id, patient_id=patient.id)

@router.post('/doctors/signup', response_model=LoginResponse)
async def signup_doctor(payload: SignupRequest, session: AsyncSession = Depends(get_session)):
    return await _signup('doctor', payload, session)

@router.post('/hospitals/signup', response_model=LoginResponse)
async def signup_hospital(payload: SignupRequest, session: AsyncSession = Depends(get_session)):
    return await _signup('hospital', payload, session)

async def _signup(role: str, payload: SignupRequest, session: AsyncSession) -> LoginResponse:
    mobile = normalize_mobile(payload.mobile)
    existing = await session.execute(
        select(Account).where(Account.role == role, Account.mobile == mobile)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail='Mobile already registered')
    account = Account(
        role=role,
        mobile=mobile,
        password_hash=hash_password(payload.password),
        patient_id=None,
    )
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return LoginResponse(role=role, account_id=account.id, patient_id=None)

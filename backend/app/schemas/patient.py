from pydantic import BaseModel, Field

class PatientCreate(BaseModel):
    name: str
    age: int | None = None
    sex: str | None = None
    contact: str | None = None
    mobile: str | None = None
    password: str | None = None

class PatientOut(BaseModel):
    id: int
    name: str
    age: int | None = None
    sex: str | None = None
    contact_masked: str | None = None

class PatientProfileOut(BaseModel):
    patient_id: int
    profile: dict
    version: int
    created_at: str | None = None

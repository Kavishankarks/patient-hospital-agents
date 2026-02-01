from pydantic import BaseModel

class LoginRequest(BaseModel):
    mobile: str
    password: str

class SignupRequest(BaseModel):
    mobile: str
    password: str

class LoginResponse(BaseModel):
    status: str = 'ok'
    role: str
    account_id: int
    patient_id: int | None = None

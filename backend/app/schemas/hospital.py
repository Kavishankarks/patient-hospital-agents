from pydantic import BaseModel, Field

class HospitalOut(BaseModel):
    hospital_id: str
    name: str
    score: float
    why: list[str] = Field(default_factory=list)

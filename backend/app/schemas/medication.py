from pydantic import BaseModel, Field

class MedicationPlanIn(BaseModel):
    plan: dict

class DoseLogIn(BaseModel):
    action: str
    timestamp: str
    note: str | None = None

class AdherenceOut(BaseModel):
    taken: int
    missed: int
    skipped: int

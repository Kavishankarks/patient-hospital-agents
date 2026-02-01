from pydantic import BaseModel, Field

class PrescriptionIn(BaseModel):
    raw_text: str

class StructuredPrescription(BaseModel):
    medications: list[dict]
    clarifications: list[str] = Field(default_factory=list)

from pydantic import BaseModel, Field

class PatientProfile(BaseModel):
    conditions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    medications: list[dict] = Field(default_factory=list)
    vitals: dict = Field(default_factory=dict)
    timeline: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)

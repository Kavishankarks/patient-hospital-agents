from pydantic import BaseModel, Field

class SBAROut(BaseModel):
    situation: str
    background: str
    assessment: str
    recommendation: str
    safety: list[str] = Field(default_factory=list)


class SBARStoredOut(BaseModel):
    patient_id: int
    sbar: SBAROut
    created_at: str | None = None

class PreIntelligenceOut(BaseModel):
    risks: list[str] = Field(default_factory=list)
    interactions: list[str] = Field(default_factory=list)
    suggested_tests: list[str] = Field(default_factory=list)
    differential_hints: list[str] = Field(default_factory=list)
    safety: list[str] = Field(default_factory=list)

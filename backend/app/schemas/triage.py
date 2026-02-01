from pydantic import BaseModel, Field

class TriageOut(BaseModel):
    level: str = "GREEN"
    red_flags: list[str] = Field(default_factory=list)
    specialty_needed: str | None = None
    safety: list[str] = Field(default_factory=list)

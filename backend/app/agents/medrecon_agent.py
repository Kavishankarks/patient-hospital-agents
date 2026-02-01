from app.agents.base import BaseAgent
from pydantic import BaseModel, Field

class MedReconOut(BaseModel):
    medications: list[dict] = Field(default_factory=list)

class MedReconAgent(BaseAgent):
    PROMPT = """Normalize medication list to generic names, dedupe, include dose/frequency/route."""

    def run(self, input_text: str) -> MedReconOut:
        return self.client.generate_json(MedReconOut, self.PROMPT, input_text)

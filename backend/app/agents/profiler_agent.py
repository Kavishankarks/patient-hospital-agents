from app.agents.base import BaseAgent
from app.schemas.profile import PatientProfile

class ProfilerAgent(BaseAgent):
    PROMPT = """You are a clinical data extractor. Return structured profile JSON only."""

    def run(self, input_text: str) -> PatientProfile:
        return self.client.generate_json(PatientProfile, self.PROMPT, input_text)

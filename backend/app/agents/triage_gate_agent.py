from app.agents.base import BaseAgent
from app.schemas.triage import TriageOut

class TriageGateAgent(BaseAgent):
    PROMPT = """Classify urgency RED/AMBER/GREEN with red flags and specialty needed. Use 'possible concern' language, not a final diagnosis. Include safety list."""

    def run(self, input_text: str) -> TriageOut:
        return self.client.generate_json(TriageOut, self.PROMPT, input_text)

from app.agents.base import BaseAgent
from app.schemas.prescription import StructuredPrescription

class PrescriptionStructurerAgent(BaseAgent):
    PROMPT = """Convert doctor prescription text to strict JSON schedule + clarifications needed."""

    def run(self, input_text: str) -> StructuredPrescription:
        return self.client.generate_json(StructuredPrescription, self.PROMPT, input_text)

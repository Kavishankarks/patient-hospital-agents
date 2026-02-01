from app.agents.base import BaseAgent
from app.schemas.intelligence import SBAROut

class SummaryAgent(BaseAgent):
    PROMPT = """Produce SBAR summary for clinician. Use 'possible concern' language, not a final diagnosis. Include safety footer items."""

    def run(self, input_text: str) -> SBAROut:
        return self.client.generate_json(SBAROut, self.PROMPT, input_text)

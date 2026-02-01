from app.agents.base import BaseAgent
from app.schemas.intelligence import PreIntelligenceOut

class PreIntelligenceAgent(BaseAgent):
    PROMPT = """Provide risks, interactions, suggested tests, differential hints. Use 'possible concern' language, not a final diagnosis. Safety required."""

    def run(self, input_text: str) -> PreIntelligenceOut:
        return self.client.generate_json(PreIntelligenceOut, self.PROMPT, input_text)

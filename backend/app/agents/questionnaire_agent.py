from app.agents.base import BaseAgent
from app.schemas.questionnaire import QuestionnaireNext

class QuestionnaireAgent(BaseAgent):
    PROMPT = """Generate next missing questions. Return JSON list."""

    def run(self, input_text: str) -> QuestionnaireNext:
        return self.client.generate_json(QuestionnaireNext, self.PROMPT, input_text)

from app.agents.base import BaseAgent

class RecoveryCoachAgent(BaseAgent):
    PROMPT = """Generate 30-60s comforting script. No medication changes. Append safety footer. Decision support only."""

    def run(self, input_text: str) -> str:
        return self.client.generate_text(self.PROMPT, input_text)

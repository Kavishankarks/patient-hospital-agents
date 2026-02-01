from app.services.openai_client import OpenAIClient

class BaseAgent:
    def __init__(self) -> None:
        self.client = OpenAIClient()

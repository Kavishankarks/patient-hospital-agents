from app.services.openai_client import OpenAIClient

class TranscriptionService:
    def __init__(self) -> None:
        self.client = OpenAIClient()

    def transcribe(self, file_path: str) -> str:
        return self.client.transcribe_audio(file_path)

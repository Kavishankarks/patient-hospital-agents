from app.services.openai_client import OpenAIClient
from app.utils.files import save_upload

class TTSService:
    def __init__(self) -> None:
        self.client = OpenAIClient()

    def synthesize(self, text: str, voice: str = 'alloy') -> str:
        output_path = save_upload(b'', 'coach.mp3')
        return self.client.tts(text, voice, output_path)

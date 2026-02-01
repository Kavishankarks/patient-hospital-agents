from pydantic import BaseModel

class CoachGenerateOut(BaseModel):
    script_text: str
    audio_path: str

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL_TEXT: str = 'gpt-4.1-mini'
    OPENAI_MODEL_REASONING: str | None = None
    OPENAI_MODEL_TTS: str = 'gpt-4o-mini-tts'
    OPENAI_MODEL_STT: str = 'whisper-1'
    DATABASE_URL: str = 'sqlite+aiosqlite:///./app.db'
    REDIS_URL: str | None = None
    MCP_HOSPITAL_BASE_URL: str = 'http://localhost:9001'
    UPLOAD_DIR: str = './data/uploads'
    NVIDIA_NIM_API_KEY: str | None = None
    NVIDIA_NIM_PAGE_ELEMENTS_URL: str = 'https://ai.api.nvidia.com/v1/cv/nvidia/nemoretriever-ocr-v1'

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()

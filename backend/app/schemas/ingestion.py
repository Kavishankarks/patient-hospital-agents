from pydantic import BaseModel

class DocumentOut(BaseModel):
    document_id: int
    extracted_text: str | None = None

class TranscriptOut(BaseModel):
    transcript_id: int
    text: str


class DocumentDetailOut(BaseModel):
    document_id: int
    mime_type: str
    has_text: bool
    text_preview: str | None = None

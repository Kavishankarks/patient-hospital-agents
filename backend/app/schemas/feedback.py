from pydantic import BaseModel

class FeedbackIn(BaseModel):
    trace_id: str
    rating: str
    comment: str | None = None

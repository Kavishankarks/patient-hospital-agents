from pydantic import BaseModel

class AuditOut(BaseModel):
    trace_id: str
    actor: str
    action: str
    created_at: str

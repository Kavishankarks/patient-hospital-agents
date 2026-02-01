from sqlalchemy import Integer, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trace_id: Mapped[str] = mapped_column(String(100))
    patient_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('patients.id'), nullable=True)
    actor: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(200))
    input_meta_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_meta_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

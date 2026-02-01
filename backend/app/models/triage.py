from sqlalchemy import Integer, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base

class TriageResult(Base):
    __tablename__ = 'triage_results'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey('patients.id'))
    level: Mapped[str] = mapped_column(String(20))
    red_flags_json: Mapped[dict] = mapped_column(JSON)
    specialty_needed: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

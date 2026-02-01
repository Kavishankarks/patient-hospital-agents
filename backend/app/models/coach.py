from sqlalchemy import Integer, DateTime, ForeignKey, Text, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base

class DoctorAdvicePack(Base):
    __tablename__ = 'doctor_advice_packs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey('patients.id'))
    plan_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('medication_plans.id'), nullable=True)
    advice_json: Mapped[dict] = mapped_column(JSON)

class CoachMessage(Base):
    __tablename__ = 'coach_messages'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey('patients.id'))
    script_text: Mapped[str] = mapped_column(Text)
    audio_path: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

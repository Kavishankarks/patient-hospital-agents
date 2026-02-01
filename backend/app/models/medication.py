from sqlalchemy import Integer, DateTime, ForeignKey, JSON, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base

class MedicationPlan(Base):
    __tablename__ = 'medication_plans'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey('patients.id'))
    plan_json: Mapped[dict] = mapped_column(JSON)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class DoseSchedule(Base):
    __tablename__ = 'dose_schedules'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey('medication_plans.id'))
    due_at: Mapped[str] = mapped_column(String(50))
    med_name: Mapped[str] = mapped_column(String(200))
    dose: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default='pending')

class DoseLog(Base):
    __tablename__ = 'dose_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dose_id: Mapped[int] = mapped_column(Integer, ForeignKey('dose_schedules.id'))
    action: Mapped[str] = mapped_column(String(20))
    timestamp: Mapped[str] = mapped_column(String(50))
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

class SideEffectLog(Base):
    __tablename__ = 'side_effect_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey('patients.id'))
    symptom: Mapped[str] = mapped_column(String(200))
    severity: Mapped[str] = mapped_column(String(20))
    timestamp: Mapped[str] = mapped_column(String(50))

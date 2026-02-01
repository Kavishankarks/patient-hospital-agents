from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Account(Base):
    __tablename__ = 'accounts'
    __table_args__ = (UniqueConstraint('role', 'mobile', name='uq_accounts_role_mobile'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(30), index=True)
    mobile: Mapped[str] = mapped_column(String(32), index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    patient_id: Mapped[int | None] = mapped_column(ForeignKey('patients.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

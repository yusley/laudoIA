from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Process(Base):
    __tablename__ = "processes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    process_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    court: Mapped[str] = mapped_column(String(255), nullable=False)
    labor_court: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    claimant: Mapped[str] = mapped_column(String(255), nullable=False)
    defendant: Mapped[str] = mapped_column(String(255), nullable=False)
    expert_name: Mapped[str] = mapped_column(String(255), nullable=False)
    expert_registry: Mapped[str] = mapped_column(String(120), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    diligence_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    diligence_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="processes")
    documents = relationship("Document", back_populates="process", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="process", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="process", cascade="all, delete-orphan")
    inspection_checklist = relationship(
        "InspectionChecklist",
        back_populates="process",
        cascade="all, delete-orphan",
        uselist=False,
    )

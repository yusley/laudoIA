from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CreditPackage(Base):
    __tablename__ = "credit_packages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    price_brl: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def estimated_report_capacity(self) -> int:
        return int(self.credit_amount)

    @property
    def price_per_estimated_report_brl(self) -> Decimal:
        if not self.credit_amount:
            return Decimal("0.00")
        return (self.price_brl / self.credit_amount).quantize(Decimal("0.01"))


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    credit_package_id: Mapped[int | None] = mapped_column(
        ForeignKey("credit_packages.id", ondelete="SET NULL"), nullable=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    provider_preference_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    external_reference: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    amount_brl: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    checkout_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="payments")
    credit_package = relationship("CreditPackage")


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    process_id: Mapped[int | None] = mapped_column(ForeignKey("processes.id", ondelete="SET NULL"), nullable=True)
    report_id: Mapped[int | None] = mapped_column(ForeignKey("reports.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    is_paid_model: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    openrouter_user_tag: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(nullable=True)
    reasoning_tokens: Mapped[int | None] = mapped_column(nullable=True)
    cached_tokens: Mapped[int | None] = mapped_column(nullable=True)
    openrouter_cost_credit: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False, default=0)
    openrouter_cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False, default=0)
    exchange_rate_usd_brl: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    openrouter_cost_brl: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    platform_revenue_brl: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    platform_margin_brl: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    platform_cost_credit: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_usage_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="usage_events")

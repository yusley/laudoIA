from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class WalletTransactionResponse(BaseModel):
    id: int
    type: str
    amount: Decimal
    balance_after: Decimal
    reference_type: str | None = None
    reference_id: str | None = None
    description: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance_credit: Decimal
    reserved_credit: Decimal
    lifetime_purchased_credit: Decimal
    lifetime_used_credit: Decimal
    created_at: datetime
    updated_at: datetime | None = None
    transactions: list[WalletTransactionResponse] = []

    model_config = {"from_attributes": True}


class CreditPackageResponse(BaseModel):
    id: int
    name: str
    credit_amount: Decimal
    price_brl: Decimal
    estimated_report_capacity: int
    price_per_estimated_report_brl: Decimal
    is_active: bool

    model_config = {"from_attributes": True}


class CreateCheckoutRequest(BaseModel):
    credit_package_id: int


class PaymentResponse(BaseModel):
    id: int
    provider: str
    status: str
    amount_brl: Decimal
    credit_amount: Decimal
    checkout_url: str | None = None
    external_reference: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class UsageEventResponse(BaseModel):
    id: int
    action: str
    model: str
    is_paid_model: bool
    openrouter_cost_credit: Decimal
    openrouter_cost_usd: Decimal
    exchange_rate_usd_brl: Decimal
    openrouter_cost_brl: Decimal
    platform_revenue_brl: Decimal
    platform_margin_brl: Decimal
    platform_cost_credit: Decimal
    status: str
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

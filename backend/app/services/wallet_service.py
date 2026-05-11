import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.billing import CreditPackage, Payment, UsageEvent
from app.models.user import User
from app.models.wallet import Wallet, WalletTransaction

ZERO = Decimal("0")
FULL_REPORT_CREDIT_COST = Decimal("1.00")
SECTION_REGENERATION_CREDIT_COST = Decimal("0.25")

COMMERCIAL_CREDIT_PACKAGES = [
    ("Plano Essencial", Decimal("25.0000"), Decimal("25.00"), 25),
    ("Plano Profissional", Decimal("100.0000"), Decimal("50.00"), 100),
    ("Plano Escala", Decimal("500.0000"), Decimal("100.00"), 500),
]


@dataclass(frozen=True)
class UsageFinancials:
    openrouter_cost_usd: Decimal
    exchange_rate_usd_brl: Decimal
    openrouter_cost_brl: Decimal
    platform_revenue_brl: Decimal
    platform_margin_brl: Decimal
    platform_cost_credit: Decimal


def quantize_credit(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def quantize_brl(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def quantize_usd(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def ensure_wallet(db: Session, user: User) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if wallet:
        return wallet

    wallet = Wallet(
        user_id=user.id,
        balance_credit=ZERO,
        reserved_credit=ZERO,
        lifetime_purchased_credit=ZERO,
        lifetime_used_credit=ZERO,
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


def seed_credit_packages(db: Session) -> None:
    active_package_names = {name for name, _, _, _ in COMMERCIAL_CREDIT_PACKAGES}
    db.query(CreditPackage).filter(CreditPackage.name.notin_(active_package_names)).update(
        {"is_active": False},
        synchronize_session=False,
    )

    for name, credit_amount, price_brl, _estimated_reports in COMMERCIAL_CREDIT_PACKAGES:
        exists = db.query(CreditPackage).filter(CreditPackage.name == name).first()
        if exists:
            exists.credit_amount = credit_amount
            exists.price_brl = price_brl
            exists.is_active = True
            continue
        db.add(
            CreditPackage(
                name=name,
                credit_amount=credit_amount,
                price_brl=price_brl,
                is_active=True,
            )
        )
    db.commit()


def create_wallet_transaction(
    db: Session,
    wallet: Wallet,
    tx_type: str,
    amount: Decimal,
    reference_type: str | None = None,
    reference_id: str | None = None,
    description: str | None = None,
    metadata: dict | None = None,
) -> WalletTransaction:
    transaction = WalletTransaction(
        wallet_id=wallet.id,
        type=tx_type,
        amount=quantize_credit(amount),
        balance_after=quantize_credit(wallet.balance_credit),
        reference_type=reference_type,
        reference_id=reference_id,
        description=description,
        metadata_json=json.dumps(metadata or {}, ensure_ascii=True),
    )
    db.add(transaction)
    return transaction


def list_active_credit_packages(db: Session) -> list[CreditPackage]:
    return (
        db.query(CreditPackage)
        .filter(CreditPackage.is_active.is_(True))
        .order_by(CreditPackage.price_brl.asc())
        .all()
    )


def estimate_platform_cost(model: str) -> Decimal:
    return estimate_action_cost(model, "report_generate")


def estimate_action_cost(model: str, action: str) -> Decimal:
    if not is_paid_model(model):
        return ZERO
    if action == "section_regenerate":
        return SECTION_REGENERATION_CREDIT_COST
    return FULL_REPORT_CREDIT_COST


def calculate_usage_financials(model: str, openrouter_cost_usd: Decimal, action: str) -> UsageFinancials:
    exchange_rate = Decimal(str(settings.USD_BRL_RATE))
    credit_value_brl = Decimal(str(settings.CREDIT_VALUE_BRL))
    margin_multiplier = Decimal(str(settings.PLATFORM_MARGIN_MULTIPLIER))
    openrouter_cost_usd = quantize_usd(openrouter_cost_usd)
    openrouter_cost_brl = quantize_brl(openrouter_cost_usd * exchange_rate)

    if not is_paid_model(model):
        return UsageFinancials(
            openrouter_cost_usd=openrouter_cost_usd,
            exchange_rate_usd_brl=exchange_rate,
            openrouter_cost_brl=openrouter_cost_brl,
            platform_revenue_brl=ZERO,
            platform_margin_brl=quantize_brl(ZERO - openrouter_cost_brl),
            platform_cost_credit=ZERO,
        )

    minimum_cost = estimate_action_cost(model, action)
    calculated_brl = openrouter_cost_brl * margin_multiplier
    calculated_credit = quantize_credit(calculated_brl / credit_value_brl) if credit_value_brl > ZERO else minimum_cost
    platform_cost_credit = calculated_credit if calculated_credit > minimum_cost else minimum_cost
    platform_revenue_brl = quantize_brl(platform_cost_credit * credit_value_brl)

    return UsageFinancials(
        openrouter_cost_usd=openrouter_cost_usd,
        exchange_rate_usd_brl=exchange_rate,
        openrouter_cost_brl=openrouter_cost_brl,
        platform_revenue_brl=platform_revenue_brl,
        platform_margin_brl=quantize_brl(platform_revenue_brl - openrouter_cost_brl),
        platform_cost_credit=platform_cost_credit,
    )


def calculate_actual_platform_cost(model: str, openrouter_cost_credit: Decimal, action: str) -> Decimal:
    return calculate_usage_financials(model, openrouter_cost_credit, action).platform_cost_credit


def is_paid_model(model: str) -> bool:
    return not (model == "openrouter/owl-alpha" or model == "openrouter/free" or model.endswith(":free"))


def reserve_for_paid_model(db: Session, wallet: Wallet, model: str, reference_id: str, action: str) -> Decimal:
    if not is_paid_model(model):
        return ZERO

    reserve_amount = estimate_action_cost(model, action)
    available = wallet.balance_credit - wallet.reserved_credit
    if available < reserve_amount:
        raise HTTPException(
            status_code=402,
            detail="Saldo insuficiente para usar este modelo pago. Compre creditos antes de continuar.",
        )

    wallet.reserved_credit = quantize_credit(wallet.reserved_credit + reserve_amount)
    create_wallet_transaction(
        db,
        wallet,
        "reservation",
        reserve_amount,
        reference_type="report_generation",
        reference_id=reference_id,
        description=f"Reserva para uso do modelo {model}",
        metadata={"model": model, "action": action},
    )
    db.add(wallet)
    db.flush()
    return reserve_amount


def settle_usage_cost(
    db: Session,
    wallet: Wallet,
    actual_platform_cost: Decimal,
    reserved_amount: Decimal,
    reference_id: str,
    model: str,
) -> None:
    reserved_amount = quantize_credit(reserved_amount)
    actual_platform_cost = quantize_credit(actual_platform_cost)

    if reserved_amount > ZERO:
        wallet.reserved_credit = quantize_credit(wallet.reserved_credit - reserved_amount)

    if actual_platform_cost > ZERO:
        available = wallet.balance_credit
        if available < actual_platform_cost:
            raise HTTPException(
                status_code=402,
                detail="Saldo insuficiente para liquidar o custo desta geracao. Adicione creditos e tente novamente.",
            )
        wallet.balance_credit = quantize_credit(wallet.balance_credit - actual_platform_cost)
        wallet.lifetime_used_credit = quantize_credit(wallet.lifetime_used_credit + actual_platform_cost)
        create_wallet_transaction(
            db,
            wallet,
            "debit",
            -actual_platform_cost,
            reference_type="report_generation",
            reference_id=reference_id,
            description=f"Consumo do modelo {model}",
            metadata={"model": model},
        )

    if reserved_amount > actual_platform_cost:
        released = quantize_credit(reserved_amount - actual_platform_cost)
        create_wallet_transaction(
            db,
            wallet,
            "reservation_release",
            released,
            reference_type="report_generation",
            reference_id=reference_id,
            description="Liberacao de reserva nao utilizada",
            metadata={"model": model},
        )

    db.add(wallet)


def release_reservation(db: Session, wallet: Wallet, reserved_amount: Decimal, reference_id: str, model: str) -> None:
    reserved_amount = quantize_credit(reserved_amount)
    if reserved_amount <= ZERO:
        return
    wallet.reserved_credit = quantize_credit(max(ZERO, wallet.reserved_credit - reserved_amount))
    create_wallet_transaction(
        db,
        wallet,
        "reservation_release",
        reserved_amount,
        reference_type="report_generation",
        reference_id=reference_id,
        description="Liberacao de reserva por falha na geracao",
        metadata={"model": model},
    )
    db.add(wallet)


def create_pending_payment(
    db: Session,
    user: User,
    package: CreditPackage,
    provider: str,
    external_reference: str,
    checkout_url: str | None,
    provider_preference_id: str | None,
    raw_payload: dict | None,
) -> Payment:
    payment = Payment(
        user_id=user.id,
        credit_package_id=package.id,
        provider=provider,
        provider_payment_id=None,
        provider_preference_id=provider_preference_id,
        external_reference=external_reference,
        status="pending",
        amount_brl=quantize_brl(package.price_brl),
        credit_amount=quantize_credit(package.credit_amount),
        checkout_url=checkout_url,
        raw_payload=json.dumps(raw_payload or {}, ensure_ascii=True),
    )
    db.add(payment)
    db.flush()
    return payment


def apply_paid_payment(db: Session, payment: Payment) -> Payment:
    if payment.status == "paid":
        return payment

    wallet = db.query(Wallet).filter(Wallet.user_id == payment.user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Carteira do usuario nao encontrada.")

    wallet.balance_credit = quantize_credit(wallet.balance_credit + payment.credit_amount)
    wallet.lifetime_purchased_credit = quantize_credit(wallet.lifetime_purchased_credit + payment.credit_amount)
    payment.status = "paid"

    create_wallet_transaction(
        db,
        wallet,
        "topup",
        payment.credit_amount,
        reference_type="payment",
        reference_id=str(payment.id),
        description="Recarga de creditos aprovada",
        metadata={"payment_id": payment.id},
    )
    db.add(wallet)
    db.add(payment)
    return payment

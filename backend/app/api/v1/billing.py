from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.billing import CreditPackage, Payment, UsageEvent
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.billing import (
    CreateCheckoutRequest,
    CreditPackageResponse,
    PaymentResponse,
    UsageEventResponse,
    WalletResponse,
)
from app.services.payment_service import create_mercado_pago_checkout, process_mercado_pago_webhook
from app.services.wallet_service import ensure_wallet, list_active_credit_packages

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/wallet", response_model=WalletResponse)
def get_wallet(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = ensure_wallet(db, current_user)
    return (
        db.query(Wallet)
        .options(joinedload(Wallet.transactions))
        .filter(Wallet.id == wallet.id)
        .first()
    )


@router.get("/packages", response_model=list[CreditPackageResponse])
def get_credit_packages(db: Session = Depends(get_db)):
    return list_active_credit_packages(db)


@router.get("/payments", response_model=list[PaymentResponse])
def list_payments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )


@router.post("/checkout", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_checkout(
    payload: CreateCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    package = (
        db.query(CreditPackage)
        .filter(CreditPackage.id == payload.credit_package_id, CreditPackage.is_active.is_(True))
        .first()
    )
    if not package:
        raise HTTPException(status_code=404, detail="Pacote de creditos nao encontrado.")
    return await create_mercado_pago_checkout(db, current_user, package)


@router.get("/usage", response_model=list[UsageEventResponse])
def list_usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(UsageEvent)
        .filter(UsageEvent.user_id == current_user.id)
        .order_by(UsageEvent.created_at.desc())
        .limit(50)
        .all()
    )


@router.post("/webhooks/mercado-pago", status_code=status.HTTP_204_NO_CONTENT)
async def mercado_pago_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    payload = {}
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    await process_mercado_pago_webhook(db, payload, dict(request.query_params))
    return None

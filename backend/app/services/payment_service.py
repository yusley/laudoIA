import json
import uuid

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.billing import CreditPackage, Payment
from app.models.user import User
from app.services.wallet_service import apply_paid_payment, create_pending_payment


async def create_mercado_pago_checkout(
    db: Session,
    user: User,
    package: CreditPackage,
) -> Payment:
    if not settings.MERCADO_PAGO_ACCESS_TOKEN:
        raise HTTPException(status_code=400, detail="MERCADO_PAGO_ACCESS_TOKEN nao configurado.")

    external_reference = f"credit_{user.id}_{package.id}_{uuid.uuid4().hex[:12]}"
    body = {
        "items": [
            {
                "title": package.name,
                "description": (
                    f"{package.credit_amount} creditos no LaudoIA Pericial. "
                    f"Media aproximada: mais ou menos {package.estimated_report_capacity} laudos."
                ),
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(package.price_brl),
            }
        ],
        "payer": {
            "name": user.name,
            "email": user.email,
        },
        "external_reference": external_reference,
        "notification_url": settings.MERCADO_PAGO_WEBHOOK_URL,
        "back_urls": {
            "success": settings.APP_URL,
            "pending": settings.APP_URL,
            "failure": settings.APP_URL,
        },
        "auto_return": "approved",
    }

    headers = {
        "Authorization": f"Bearer {settings.MERCADO_PAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.mercadopago.com/checkout/preferences",
            headers=headers,
            json=body,
        )

    if response.status_code >= 400:
        raise HTTPException(status_code=400, detail=f"Falha ao criar checkout Mercado Pago: {response.text[:300]}")

    data = response.json()
    payment = create_pending_payment(
        db=db,
        user=user,
        package=package,
        provider="mercado_pago",
        external_reference=external_reference,
        checkout_url=data.get("init_point"),
        provider_preference_id=data.get("id"),
        raw_payload=data,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


async def process_mercado_pago_webhook(db: Session, payload: dict, query_params: dict) -> None:
    topic = payload.get("type") or payload.get("topic") or query_params.get("topic")
    resource_id = (
        payload.get("data", {}).get("id")
        or payload.get("id")
        or query_params.get("id")
        or query_params.get("data.id")
    )

    if topic and "payment" not in str(topic):
        return
    if not resource_id:
        return
    if not settings.MERCADO_PAGO_ACCESS_TOKEN:
        return

    headers = {"Authorization": f"Bearer {settings.MERCADO_PAGO_ACCESS_TOKEN}"}
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(f"https://api.mercadopago.com/v1/payments/{resource_id}", headers=headers)
    if response.status_code >= 400:
        return

    payment_data = response.json()
    external_reference = payment_data.get("external_reference")
    if not external_reference:
        return

    payment = db.query(Payment).filter(Payment.external_reference == external_reference).first()
    if not payment:
        return

    payment.provider_payment_id = str(payment_data.get("id"))
    payment.raw_payload = json.dumps(payment_data, ensure_ascii=True)
    status = payment_data.get("status", "pending")
    payment.status = status

    if status == "approved":
        apply_paid_payment(db, payment)

    db.add(payment)
    db.commit()

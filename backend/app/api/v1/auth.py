from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.user_service import is_admin_email
from app.services.wallet_service import ensure_wallet

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ja cadastrado.")

    try:
        hashed_password = get_password_hash(payload.password)
    except ValueError as exc:
        detail = str(exc)
        if "72 bytes" in detail:
            detail = "A senha informada e muito longa para o metodo atual de seguranca. Tente uma senha menor."
        raise HTTPException(status_code=400, detail=detail) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Falha interna ao processar a senha.") from exc

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hashed_password,
        is_admin=is_admin_email(payload.email),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    ensure_wallet(db, user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")

    try:
        is_valid = verify_password(payload.password, user.hashed_password)
    except ValueError as exc:
        detail = str(exc)
        if "Formato de senha armazenada nao suportado." in detail:
            detail = "Nao foi possivel validar esta conta com o formato de senha atual. Cadastre uma nova conta ou redefina a senha."
        raise HTTPException(status_code=400, detail=detail) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Falha interna ao verificar a senha.") from exc

    if not is_valid:
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"
PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 390000
PASSWORD_SCHEME = "pbkdf2_sha256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith(f"{PASSWORD_SCHEME}$"):
        try:
            _, iterations, salt, digest = hashed_password.split("$", 3)
            calculated = hashlib.pbkdf2_hmac(
                PBKDF2_ALGORITHM,
                plain_password.encode("utf-8"),
                base64.urlsafe_b64decode(salt.encode("ascii")),
                int(iterations),
            )
            expected = base64.urlsafe_b64decode(digest.encode("ascii"))
            return hmac.compare_digest(calculated, expected)
        except (ValueError, TypeError):
            return False

    raise ValueError("Formato de senha armazenada nao suportado.")


def get_password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    encoded_salt = base64.urlsafe_b64encode(salt).decode("ascii")
    encoded_digest = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"{PASSWORD_SCHEME}${PBKDF2_ITERATIONS}${encoded_salt}${encoded_digest}"


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"exp": expire, "sub": subject}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def safe_decode_token(token: str) -> dict | None:
    try:
        return decode_token(token)
    except JWTError:
        return None

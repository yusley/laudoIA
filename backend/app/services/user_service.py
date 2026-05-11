from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User


def get_admin_emails() -> set[str]:
    return {
        email.strip().lower()
        for email in settings.ADMIN_EMAILS.split(",")
        if email.strip()
    }


def seed_admin_users(db: Session) -> None:
    admin_emails = get_admin_emails()
    if not admin_emails:
        return

    users = db.query(User).filter(User.email.in_(admin_emails)).all()
    changed = False
    for user in users:
        if not user.is_admin:
            user.is_admin = True
            db.add(user)
            changed = True
    if changed:
        db.commit()


def is_admin_email(email: str) -> bool:
    return email.strip().lower() in get_admin_emails()

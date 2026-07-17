from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models import User
from app.services.auth import decode_access_token


def get_database_session() -> Session:
    yield from get_db()


def require_platform_admin(
    x_platform_admin_token: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> None:
    if authorization and authorization.lower().startswith("bearer "):
        payload = decode_access_token(authorization.split(" ", 1)[1].strip())
        if payload:
            return

    if not x_platform_admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing platform admin token.",
        )

    if x_platform_admin_token != settings.platform_admin_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid platform admin token.",
        )


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_database_session),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    payload = decode_access_token(authorization.split(" ", 1)[1].strip())
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired bearer token.",
        )

    user_id = payload.get("sub")
    try:
        parsed_user_id = UUID(user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token subject.",
        ) from exc

    user = db.scalar(select(User).where(User.id == parsed_user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active.",
        )
    return user

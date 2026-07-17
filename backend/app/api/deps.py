from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db


def get_database_session() -> Session:
    yield from get_db()


def require_platform_admin(
    x_platform_admin_token: str | None = Header(default=None),
) -> None:
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

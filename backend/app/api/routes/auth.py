from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_database_session
from app.core.config import settings
from app.models import Company, User
from app.schemas.auth import AuthenticatedUser, LoginRequest, LoginResponse
from app.services.auth import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_database_session),
) -> LoginResponse:
    identifier = payload.identifier.strip().lower()
    user = db.scalar(
        select(User).where(
            or_(
                User.email == identifier,
                User.phone == payload.identifier.strip(),
            )
        )
    )

    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials.",
        )

    company = db.get(Company, user.company_id)
    if not company or company.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company is not active.",
        )

    return LoginResponse(
        access_token=create_access_token(user.id, user.company_id, user.role),
        expires_in_seconds=settings.auth_token_ttl_seconds,
        user=_authenticated_user(user, company),
    )


@router.get("/me", response_model=AuthenticatedUser)
def me(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session),
) -> AuthenticatedUser:
    company = db.get(Company, user.company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )
    return _authenticated_user(user, company)


def _authenticated_user(user: User, company: Company) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=user.id,
        company_id=user.company_id,
        company_name=company.name,
        name=user.name,
        phone=user.phone,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )

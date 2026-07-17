from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models import Company, Project, ProjectUser, User
from app.services.auth import decode_access_token

COMPANY_ADMIN_ROLES = {"owner", "admin", "company_admin"}
PROJECT_ENTRY_PERMISSION_FIELDS = {
    "progress": "can_enter_progress",
    "manpower": "can_enter_manpower",
    "materials": "can_enter_materials",
}


def get_database_session() -> Session:
    yield from get_db()


class AuthContext:
    def __init__(self, user: User | None = None, is_platform_admin: bool = False) -> None:
        self.user = user
        self.is_platform_admin = is_platform_admin


def get_auth_context(
    x_platform_admin_token: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_database_session),
) -> AuthContext:
    if x_platform_admin_token:
        if x_platform_admin_token != settings.platform_admin_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid platform admin token.",
            )
        return AuthContext(is_platform_admin=True)

    if authorization and authorization.lower().startswith("bearer "):
        user = _load_user_from_authorization_header(db, authorization)
        return AuthContext(user=user)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing authentication credentials.",
    )


def require_platform_admin(auth: AuthContext = Depends(get_auth_context)) -> None:
    if not auth.is_platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform admin access is required.",
        )


def get_current_user(auth: AuthContext = Depends(get_auth_context)) -> User:
    if auth.is_platform_admin or not auth.user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User login is required.",
        )
    return auth.user


def require_company_member(
    db: Session,
    company_id: UUID,
    auth: AuthContext,
) -> User | None:
    company = _require_company_exists(db, company_id)
    if auth.is_platform_admin:
        return None

    if not auth.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User login is required.",
        )

    if auth.user.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this company.",
        )

    return auth.user


def require_company_admin_access(
    db: Session,
    company_id: UUID,
    auth: AuthContext,
) -> User | None:
    user = require_company_member(db, company_id, auth)
    if auth.is_platform_admin:
        return None

    if not user or user.role not in COMPANY_ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company owner/admin access is required.",
        )
    return user


def require_project_dashboard_access(
    db: Session,
    company_id: UUID,
    project_id: UUID,
    auth: AuthContext,
) -> Project:
    return _require_project_access(
        db=db,
        company_id=company_id,
        project_id=project_id,
        auth=auth,
        permission_field=None,
        allow_dashboard_permission=True,
        allow_any_entry_permission=True,
    )


def require_project_entry_access(
    db: Session,
    company_id: UUID,
    project_id: UUID,
    auth: AuthContext,
    entry_type: str,
    *,
    allow_dashboard_permission: bool = False,
) -> Project:
    permission_field = PROJECT_ENTRY_PERMISSION_FIELDS[entry_type]
    return _require_project_access(
        db=db,
        company_id=company_id,
        project_id=project_id,
        auth=auth,
        permission_field=permission_field,
        allow_dashboard_permission=allow_dashboard_permission,
        allow_any_entry_permission=False,
    )


def _require_project_access(
    db: Session,
    company_id: UUID,
    project_id: UUID,
    auth: AuthContext,
    permission_field: str | None,
    *,
    allow_dashboard_permission: bool,
    allow_any_entry_permission: bool,
) -> Project:
    project = _require_project_in_company(db, company_id, project_id)
    if auth.is_platform_admin:
        return project

    user = require_company_member(db, company_id, auth)
    if user and user.role in COMPANY_ADMIN_ROLES:
        return project
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User login is required.",
        )

    assignment = db.scalar(
        select(ProjectUser)
        .where(ProjectUser.project_id == project_id)
        .where(ProjectUser.user_id == user.id)
    )
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this project.",
        )

    if allow_dashboard_permission and assignment.can_view_dashboard:
        return project

    if permission_field and bool(getattr(assignment, permission_field)):
        return project

    if allow_any_entry_permission and (
        assignment.can_enter_progress
        or assignment.can_enter_manpower
        or assignment.can_enter_materials
    ):
        return project

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Your project role does not allow this action.",
    )


def _load_user_from_authorization_header(db: Session, authorization: str) -> User:
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


def _require_company_exists(db: Session, company_id: UUID) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )
    return company


def _require_project_in_company(db: Session, company_id: UUID, project_id: UUID) -> Project:
    project = db.get(Project, project_id)
    if not project or project.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found for this company.",
        )
    return project

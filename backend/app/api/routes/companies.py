from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_database_session, require_platform_admin
from app.models import Company, Project, ProjectUser, User
from app.schemas.company import CompanyCreate, CompanyRead
from app.schemas.project import ProjectCreate, ProjectRead
from app.schemas.project_user import ProjectUserCreate, ProjectUserRead
from app.schemas.user import UserCreate, UserRead

router = APIRouter(
    prefix="/companies",
    dependencies=[Depends(require_platform_admin)],
)


@router.post(
    "",
    response_model=CompanyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    payload: CompanyCreate,
    db: Session = Depends(get_database_session),
) -> Company:
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_database_session)) -> list[Company]:
    return list(db.scalars(select(Company).order_by(Company.created_at.desc())).all())


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: UUID,
    db: Session = Depends(get_database_session),
) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )
    return company


@router.post(
    "/{company_id}/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_company_user(
    company_id: UUID,
    payload: UserCreate,
    db: Session = Depends(get_database_session),
) -> User:
    _require_company(db, company_id)

    user = User(company_id=company_id, **payload.model_dump())
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User phone or email already exists for this company.",
        ) from exc

    db.refresh(user)
    return user


@router.get("/{company_id}/users", response_model=list[UserRead])
def list_company_users(
    company_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[User]:
    _require_company(db, company_id)

    return list(
        db.scalars(
            select(User)
            .where(User.company_id == company_id)
            .order_by(User.created_at.desc())
        ).all()
    )


@router.post(
    "/{company_id}/projects",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_company_project(
    company_id: UUID,
    payload: ProjectCreate,
    db: Session = Depends(get_database_session),
) -> Project:
    _require_company(db, company_id)

    project = Project(company_id=company_id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{company_id}/projects", response_model=list[ProjectRead])
def list_company_projects(
    company_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[Project]:
    _require_company(db, company_id)

    return list(
        db.scalars(
            select(Project)
            .where(Project.company_id == company_id)
            .order_by(Project.created_at.desc())
        ).all()
    )


@router.post(
    "/{company_id}/projects/{project_id}/users",
    response_model=ProjectUserRead,
    status_code=status.HTTP_201_CREATED,
)
def assign_user_to_project(
    company_id: UUID,
    project_id: UUID,
    payload: ProjectUserCreate,
    db: Session = Depends(get_database_session),
) -> ProjectUser:
    _require_company(db, company_id)
    _require_project_in_company(db, company_id, project_id)
    _require_user_in_company(db, company_id, payload.user_id)

    assignment = ProjectUser(project_id=project_id, **payload.model_dump())
    db.add(assignment)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already assigned to this project.",
        ) from exc

    db.refresh(assignment)
    return assignment


@router.get(
    "/{company_id}/projects/{project_id}/users",
    response_model=list[ProjectUserRead],
)
def list_project_users(
    company_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[ProjectUser]:
    _require_company(db, company_id)
    _require_project_in_company(db, company_id, project_id)

    return list(
        db.scalars(
            select(ProjectUser)
            .where(ProjectUser.project_id == project_id)
            .order_by(ProjectUser.created_at.desc())
        ).all()
    )


def _require_company(db: Session, company_id: UUID) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )
    return company


def _require_project_in_company(
    db: Session,
    company_id: UUID,
    project_id: UUID,
) -> Project:
    project = db.get(Project, project_id)
    if not project or project.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found for this company.",
        )
    return project


def _require_user_in_company(
    db: Session,
    company_id: UUID,
    user_id: UUID,
) -> User:
    user = db.get(User, user_id)
    if not user or user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for this company.",
        )
    return user

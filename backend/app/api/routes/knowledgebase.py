from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from io import BytesIO

from app.api.deps import get_database_session, require_platform_admin
from app.models import (
    Activity,
    ActivitySynonym,
    BOQItem,
    Company,
    Project,
    ProjectKnowledgeUpload,
    ProjectLocation,
    ProjectScheduleItem,
    Unit,
    User,
)
from app.schemas.knowledgebase import (
    ActivityCreate,
    ActivityRead,
    ActivitySynonymCreate,
    ActivitySynonymRead,
    BOQItemCreate,
    BOQItemRead,
    KnowledgeTemplateImportResult,
    ProjectKnowledgeUploadCreate,
    ProjectKnowledgeUploadRead,
    ProjectLocationCreate,
    ProjectLocationRead,
    ProjectScheduleItemCreate,
    ProjectScheduleItemRead,
    UnitCreate,
    UnitRead,
)
from app.services.knowledgebase_templates import build_template_workbook, import_template

router = APIRouter(
    prefix="/companies/{company_id}",
    dependencies=[Depends(require_platform_admin)],
)


@router.get("/knowledgebase/templates/{template_type}")
def download_knowledgebase_template(
    company_id: UUID,
    template_type: str,
    db: Session = Depends(get_database_session),
) -> StreamingResponse:
    _require_company(db, company_id)
    try:
        content = build_template_workbook(template_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    normalized_name = template_type.strip().lower().replace("-", "_")
    filename = f"{normalized_name}_template.xlsx"
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/projects/{project_id}/knowledge-uploads/import",
    response_model=KnowledgeTemplateImportResult,
)
async def import_knowledgebase_template(
    company_id: UUID,
    project_id: UUID,
    upload_type: str = Form(...),
    uploaded_by: UUID | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_database_session),
) -> KnowledgeTemplateImportResult:
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .xlsx template files are supported.",
        )

    content = await file.read()
    try:
        result = import_template(
            db=db,
            company_id=company_id,
            project_id=project_id,
            upload_type=upload_type,
            file_name=file.filename,
            content=content,
            uploaded_by=uploaded_by,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return KnowledgeTemplateImportResult.model_validate(result)


@router.post("/units", response_model=UnitRead, status_code=status.HTTP_201_CREATED)
def create_unit(
    company_id: UUID,
    payload: UnitCreate,
    db: Session = Depends(get_database_session),
) -> Unit:
    _require_company(db, company_id)
    unit = Unit(company_id=company_id, **payload.model_dump())
    return _commit_or_conflict(db, unit, "Unit already exists for this company.")


@router.get("/units", response_model=list[UnitRead])
def list_units(
    company_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[Unit]:
    _require_company(db, company_id)
    return list(
        db.scalars(select(Unit).where(Unit.company_id == company_id).order_by(Unit.name)).all()
    )


@router.post(
    "/activities",
    response_model=ActivityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_activity(
    company_id: UUID,
    payload: ActivityCreate,
    db: Session = Depends(get_database_session),
) -> Activity:
    _require_company(db, company_id)
    if payload.default_unit_id:
        _require_unit_in_company(db, company_id, payload.default_unit_id)

    activity = Activity(company_id=company_id, **payload.model_dump())
    return _commit_or_conflict(db, activity, "Activity already exists for this company.")


@router.get("/activities", response_model=list[ActivityRead])
def list_activities(
    company_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[Activity]:
    _require_company(db, company_id)
    return list(
        db.scalars(
            select(Activity).where(Activity.company_id == company_id).order_by(Activity.name)
        ).all()
    )


@router.post(
    "/activities/{activity_id}/synonyms",
    response_model=ActivitySynonymRead,
    status_code=status.HTTP_201_CREATED,
)
def create_activity_synonym(
    company_id: UUID,
    activity_id: UUID,
    payload: ActivitySynonymCreate,
    db: Session = Depends(get_database_session),
) -> ActivitySynonym:
    _require_activity_in_company(db, company_id, activity_id)
    synonym = ActivitySynonym(
        company_id=company_id,
        activity_id=activity_id,
        **payload.model_dump(),
    )
    return _commit_or_conflict(db, synonym, "Synonym already exists for this activity.")


@router.get(
    "/activities/{activity_id}/synonyms",
    response_model=list[ActivitySynonymRead],
)
def list_activity_synonyms(
    company_id: UUID,
    activity_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[ActivitySynonym]:
    _require_activity_in_company(db, company_id, activity_id)
    return list(
        db.scalars(
            select(ActivitySynonym)
            .where(ActivitySynonym.activity_id == activity_id)
            .order_by(ActivitySynonym.synonym)
        ).all()
    )


@router.post(
    "/projects/{project_id}/locations",
    response_model=ProjectLocationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project_location(
    company_id: UUID,
    project_id: UUID,
    payload: ProjectLocationCreate,
    db: Session = Depends(get_database_session),
) -> ProjectLocation:
    _require_project_in_company(db, company_id, project_id)
    if payload.parent_location_id:
        _require_location_in_project(db, company_id, project_id, payload.parent_location_id)

    location = ProjectLocation(
        company_id=company_id,
        project_id=project_id,
        **payload.model_dump(),
    )
    return _commit_or_conflict(db, location, "Location already exists under this parent.")


@router.get(
    "/projects/{project_id}/locations",
    response_model=list[ProjectLocationRead],
)
def list_project_locations(
    company_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[ProjectLocation]:
    _require_project_in_company(db, company_id, project_id)
    return list(
        db.scalars(
            select(ProjectLocation)
            .where(ProjectLocation.company_id == company_id)
            .where(ProjectLocation.project_id == project_id)
            .order_by(ProjectLocation.location_type, ProjectLocation.name)
        ).all()
    )


@router.post(
    "/projects/{project_id}/boq-items",
    response_model=BOQItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_boq_item(
    company_id: UUID,
    project_id: UUID,
    payload: BOQItemCreate,
    db: Session = Depends(get_database_session),
) -> BOQItem:
    _require_project_in_company(db, company_id, project_id)
    if payload.unit_id:
        _require_unit_in_company(db, company_id, payload.unit_id)
    if payload.activity_id:
        _require_activity_in_company(db, company_id, payload.activity_id)

    item = BOQItem(company_id=company_id, project_id=project_id, **payload.model_dump())
    return _commit_or_conflict(db, item, "BOQ item already exists for this project.")


@router.get(
    "/projects/{project_id}/boq-items",
    response_model=list[BOQItemRead],
)
def list_boq_items(
    company_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[BOQItem]:
    _require_project_in_company(db, company_id, project_id)
    return list(
        db.scalars(
            select(BOQItem)
            .where(BOQItem.company_id == company_id)
            .where(BOQItem.project_id == project_id)
            .order_by(BOQItem.item_code, BOQItem.item_description)
        ).all()
    )


@router.post(
    "/projects/{project_id}/schedule-items",
    response_model=ProjectScheduleItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule_item(
    company_id: UUID,
    project_id: UUID,
    payload: ProjectScheduleItemCreate,
    db: Session = Depends(get_database_session),
) -> ProjectScheduleItem:
    _require_project_in_company(db, company_id, project_id)
    if payload.activity_id:
        _require_activity_in_company(db, company_id, payload.activity_id)
    if payload.unit_id:
        _require_unit_in_company(db, company_id, payload.unit_id)
    if payload.area_id:
        _require_location_in_project(db, company_id, project_id, payload.area_id)
    if payload.sub_area_id:
        _require_location_in_project(db, company_id, project_id, payload.sub_area_id)

    item = ProjectScheduleItem(
        company_id=company_id,
        project_id=project_id,
        **payload.model_dump(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get(
    "/projects/{project_id}/schedule-items",
    response_model=list[ProjectScheduleItemRead],
)
def list_schedule_items(
    company_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[ProjectScheduleItem]:
    _require_project_in_company(db, company_id, project_id)
    return list(
        db.scalars(
            select(ProjectScheduleItem)
            .where(ProjectScheduleItem.company_id == company_id)
            .where(ProjectScheduleItem.project_id == project_id)
            .order_by(ProjectScheduleItem.planned_start_date, ProjectScheduleItem.activity_name)
        ).all()
    )


@router.post(
    "/projects/{project_id}/knowledge-uploads",
    response_model=ProjectKnowledgeUploadRead,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_upload_record(
    company_id: UUID,
    project_id: UUID,
    payload: ProjectKnowledgeUploadCreate,
    db: Session = Depends(get_database_session),
) -> ProjectKnowledgeUpload:
    _require_project_in_company(db, company_id, project_id)
    if payload.uploaded_by:
        _require_user_in_company(db, company_id, payload.uploaded_by)

    upload = ProjectKnowledgeUpload(
        company_id=company_id,
        project_id=project_id,
        **payload.model_dump(),
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    return upload


@router.get(
    "/projects/{project_id}/knowledge-uploads",
    response_model=list[ProjectKnowledgeUploadRead],
)
def list_knowledge_upload_records(
    company_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[ProjectKnowledgeUpload]:
    _require_project_in_company(db, company_id, project_id)
    return list(
        db.scalars(
            select(ProjectKnowledgeUpload)
            .where(ProjectKnowledgeUpload.company_id == company_id)
            .where(ProjectKnowledgeUpload.project_id == project_id)
            .order_by(ProjectKnowledgeUpload.uploaded_at.desc())
        ).all()
    )


def _commit_or_conflict[T](db: Session, entity: T, conflict_message: str) -> T:
    db.add(entity)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=conflict_message,
        ) from exc

    db.refresh(entity)
    return entity


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


def _require_user_in_company(db: Session, company_id: UUID, user_id: UUID) -> User:
    user = db.get(User, user_id)
    if not user or user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for this company.",
        )
    return user


def _require_unit_in_company(db: Session, company_id: UUID, unit_id: UUID) -> Unit:
    unit = db.get(Unit, unit_id)
    if not unit or unit.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found for this company.",
        )
    return unit


def _require_activity_in_company(
    db: Session,
    company_id: UUID,
    activity_id: UUID,
) -> Activity:
    activity = db.get(Activity, activity_id)
    if not activity or activity.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found for this company.",
        )
    return activity


def _require_location_in_project(
    db: Session,
    company_id: UUID,
    project_id: UUID,
    location_id: UUID,
) -> ProjectLocation:
    location = db.get(ProjectLocation, location_id)
    if (
        not location
        or location.company_id != company_id
        or location.project_id != project_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found for this project.",
        )
    return location

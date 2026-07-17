from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_database_session, require_platform_admin
from app.models import (
    Activity,
    AssistantConversationState,
    BOQItem,
    ManpowerEntry,
    MaterialStockBalance,
    MaterialTransaction,
    MediaFile,
    ProgressEntry,
    Project,
    ProjectLocation,
    Unit,
    User,
    WhatsAppMessage,
)
from app.schemas.reporting import (
    ManpowerEntryCreate,
    ManpowerEntryRead,
    MaterialStockBalanceCreate,
    MaterialStockBalanceRead,
    MaterialTransactionCreate,
    MaterialTransactionRead,
    MediaFileCreate,
    MediaFileRead,
    ProgressEntryCreate,
    ProgressEntryRead,
)

router = APIRouter(
    prefix="/companies/{company_id}/projects/{project_id}/reporting",
    dependencies=[Depends(require_platform_admin)],
)


@router.post(
    "/progress-entries",
    response_model=ProgressEntryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_progress_entry(
    company_id: UUID,
    project_id: UUID,
    payload: ProgressEntryCreate,
    db: Session = Depends(get_database_session),
) -> ProgressEntry:
    _validate_common_references(db, company_id, project_id, payload)
    if payload.activity_id:
        _require_activity_in_company(db, company_id, payload.activity_id)

    entry = ProgressEntry(company_id=company_id, project_id=project_id, **payload.model_dump())
    return _commit(db, entry)


@router.get("/progress-entries", response_model=list[ProgressEntryRead])
def list_progress_entries(
    company_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[ProgressEntry]:
    _require_project_in_company(db, company_id, project_id)
    return list(
        db.scalars(
            select(ProgressEntry)
            .where(ProgressEntry.company_id == company_id)
            .where(ProgressEntry.project_id == project_id)
            .order_by(ProgressEntry.work_date.desc(), ProgressEntry.created_at.desc())
        ).all()
    )


@router.post(
    "/manpower-entries",
    response_model=ManpowerEntryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_manpower_entry(
    company_id: UUID,
    project_id: UUID,
    payload: ManpowerEntryCreate,
    db: Session = Depends(get_database_session),
) -> ManpowerEntry:
    _validate_common_references(db, company_id, project_id, payload)
    entry = ManpowerEntry(company_id=company_id, project_id=project_id, **payload.model_dump())
    return _commit(db, entry)


@router.get("/manpower-entries", response_model=list[ManpowerEntryRead])
def list_manpower_entries(
    company_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[ManpowerEntry]:
    _require_project_in_company(db, company_id, project_id)
    return list(
        db.scalars(
            select(ManpowerEntry)
            .where(ManpowerEntry.company_id == company_id)
            .where(ManpowerEntry.project_id == project_id)
            .order_by(ManpowerEntry.work_date.desc(), ManpowerEntry.trade_name)
        ).all()
    )


@router.post(
    "/material-transactions",
    response_model=MaterialTransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_material_transaction(
    company_id: UUID,
    project_id: UUID,
    payload: MaterialTransactionCreate,
    db: Session = Depends(get_database_session),
) -> MaterialTransaction:
    _validate_common_references(db, company_id, project_id, payload)
    if payload.boq_item_id:
        _require_boq_item_in_project(db, company_id, project_id, payload.boq_item_id)

    entry = MaterialTransaction(
        company_id=company_id,
        project_id=project_id,
        **payload.model_dump(),
    )
    return _commit(db, entry)


@router.get("/material-transactions", response_model=list[MaterialTransactionRead])
def list_material_transactions(
    company_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[MaterialTransaction]:
    _require_project_in_company(db, company_id, project_id)
    return list(
        db.scalars(
            select(MaterialTransaction)
            .where(MaterialTransaction.company_id == company_id)
            .where(MaterialTransaction.project_id == project_id)
            .order_by(
                MaterialTransaction.transaction_date.desc(),
                MaterialTransaction.created_at.desc(),
            )
        ).all()
    )


@router.post(
    "/material-stock-balances",
    response_model=MaterialStockBalanceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_material_stock_balance(
    company_id: UUID,
    project_id: UUID,
    payload: MaterialStockBalanceCreate,
    db: Session = Depends(get_database_session),
) -> MaterialStockBalance:
    _require_project_in_company(db, company_id, project_id)
    if payload.boq_item_id:
        _require_boq_item_in_project(db, company_id, project_id, payload.boq_item_id)
    if payload.unit_id:
        _require_unit_in_company(db, company_id, payload.unit_id)

    balance = MaterialStockBalance(
        company_id=company_id,
        project_id=project_id,
        **payload.model_dump(),
    )
    return _commit(db, balance)


@router.get("/material-stock-balances", response_model=list[MaterialStockBalanceRead])
def list_material_stock_balances(
    company_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[MaterialStockBalance]:
    _require_project_in_company(db, company_id, project_id)
    return list(
        db.scalars(
            select(MaterialStockBalance)
            .where(MaterialStockBalance.company_id == company_id)
            .where(MaterialStockBalance.project_id == project_id)
            .order_by(MaterialStockBalance.material_name)
        ).all()
    )


@router.post("/media-files", response_model=MediaFileRead, status_code=status.HTTP_201_CREATED)
def create_media_file(
    company_id: UUID,
    project_id: UUID,
    payload: MediaFileCreate,
    db: Session = Depends(get_database_session),
) -> MediaFile:
    _require_project_in_company(db, company_id, project_id)
    if payload.uploaded_by:
        _require_user_in_company(db, company_id, payload.uploaded_by)
    if payload.source_whatsapp_message_id:
        _require_whatsapp_message_in_company(db, company_id, payload.source_whatsapp_message_id)

    media_file = MediaFile(company_id=company_id, project_id=project_id, **payload.model_dump())
    return _commit(db, media_file)


@router.get("/media-files", response_model=list[MediaFileRead])
def list_media_files(
    company_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[MediaFile]:
    _require_project_in_company(db, company_id, project_id)
    return list(
        db.scalars(
            select(MediaFile)
            .where(MediaFile.company_id == company_id)
            .where(MediaFile.project_id == project_id)
            .order_by(MediaFile.created_at.desc())
        ).all()
    )


def _validate_common_references(
    db: Session,
    company_id: UUID,
    project_id: UUID,
    payload,
) -> None:
    _require_project_in_company(db, company_id, project_id)
    if payload.entered_by:
        _require_user_in_company(db, company_id, payload.entered_by)
    if payload.source_whatsapp_message_id:
        _require_whatsapp_message_in_company(db, company_id, payload.source_whatsapp_message_id)
    if payload.assistant_conversation_state_id:
        _require_conversation_state_in_company(
            db,
            company_id,
            payload.assistant_conversation_state_id,
        )
    if getattr(payload, "unit_id", None):
        _require_unit_in_company(db, company_id, payload.unit_id)
    if getattr(payload, "area_id", None):
        _require_location_in_project(db, company_id, project_id, payload.area_id)
    if getattr(payload, "sub_area_id", None):
        _require_location_in_project(db, company_id, project_id, payload.sub_area_id)


def _commit[T](db: Session, entity: T) -> T:
    db.add(entity)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Record conflicts with an existing record.",
        ) from exc

    db.refresh(entity)
    return entity


def _require_project_in_company(db: Session, company_id: UUID, project_id: UUID) -> Project:
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


def _require_activity_in_company(db: Session, company_id: UUID, activity_id: UUID) -> Activity:
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
    if not location or location.company_id != company_id or location.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found for this project.",
        )
    return location


def _require_boq_item_in_project(
    db: Session,
    company_id: UUID,
    project_id: UUID,
    boq_item_id: UUID,
) -> BOQItem:
    item = db.get(BOQItem, boq_item_id)
    if not item or item.company_id != company_id or item.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BOQ item not found for this project.",
        )
    return item


def _require_whatsapp_message_in_company(
    db: Session,
    company_id: UUID,
    message_id: UUID,
) -> WhatsAppMessage:
    message = db.get(WhatsAppMessage, message_id)
    if not message or message.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp message not found for this company.",
        )
    return message


def _require_conversation_state_in_company(
    db: Session,
    company_id: UUID,
    state_id: UUID,
) -> AssistantConversationState:
    state = db.get(AssistantConversationState, state_id)
    if not state or state.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant conversation state not found for this company.",
        )
    return state

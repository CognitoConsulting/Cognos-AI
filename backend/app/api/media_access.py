from fastapi import HTTPException, status
from fastapi.responses import FileResponse, RedirectResponse, Response

from app.services.media_storage import MediaAccessResult


def media_access_response(access: MediaAccessResult) -> Response:
    if access.status == "accessible" and access.access_type == "file" and access.file_path:
        return FileResponse(
            path=str(access.file_path),
            filename=access.file_name,
            media_type=access.mime_type,
        )

    if access.status == "accessible" and access.url:
        return RedirectResponse(access.url)

    raise HTTPException(
        status_code=_media_access_error_status(access.status),
        detail=access.error_message or "Stored media is not currently accessible.",
    )


def _media_access_error_status(access_status: str) -> int:
    if access_status == "not_found":
        return status.HTTP_404_NOT_FOUND
    if access_status in {"unsupported_storage_provider", "storage_dependency_missing"}:
        return status.HTTP_501_NOT_IMPLEMENTED
    if access_status in {
        "storage_credentials_not_configured",
        "presign_failed",
        "invalid_storage_url",
    }:
        return status.HTTP_409_CONFLICT
    return status.HTTP_400_BAD_REQUEST

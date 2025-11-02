from fastapi import APIRouter, Depends, Path, UploadFile, Query
from fastapi.responses import StreamingResponse
from starlette import status

from src.services.authorization.schemas import User
from src.services.snapshot.dependencies import snapshot_service_dependency
from src.services.snapshot.schemas import (
    SnapshotItemSchema,
    SnapshotListSchema,
    SnapshotFilters,
)
from src.services.snapshot.service import SnapshotService
from src.services.token.service import decode_user_token

router = APIRouter()


@router.get("/{proctoringId}/snapshots", status_code=status.HTTP_200_OK)
async def get_proctoring_snapshots(
    proctoring_id: int = Path(alias="proctoringId"),
    snapshot_service: SnapshotService = Depends(snapshot_service_dependency),
    user: User = Depends(decode_user_token),
) -> SnapshotListSchema:
    """
    Получить все снимки для сессии прокторинга
    
    Возвращает список всех снимков с метаданными и статистикой
    """
    return await snapshot_service.get_snapshots_by_proctoring_id(
        user=user,
        proctoring_id=proctoring_id
    )


@router.get("/{proctoringId}/report", status_code=status.HTTP_200_OK)
async def download_proctoring_report(
    proctoring_id: int = Path(alias="proctoringId"),
    snapshot_service: SnapshotService = Depends(snapshot_service_dependency),
    user: User = Depends(decode_user_token),
) -> StreamingResponse:
    """
    Скачать PDF отчет по сессии прокторинга
    
    Отчет включает:
    - Информацию о студенте и предмете
    - Статистику нарушений
    - Фотографии с временными метками
    """
    pdf_buffer = await snapshot_service.generate_pdf_report(
        user=user,
        proctoring_id=proctoring_id
    )
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=proctoring_report_{proctoring_id}.pdf"
        }
    )


@router.post("/{proctoringId}/snapshot", status_code=status.HTTP_201_CREATED)
async def upload_snapshot(
    proctoring_id: int = Path(alias="proctoringId"),
    image: UploadFile = None,
    violation_type: str | None = Query(None, alias="violationType"),
    snapshot_service: SnapshotService = Depends(snapshot_service_dependency),
    user: User = Depends(decode_user_token),
) -> SnapshotItemSchema:
    """
    Загрузить новый снимок нарушения для сессии прокторинга
    
    Загружает изображение в S3/MinIO и сохраняет метаданные в БД
    """
    return await snapshot_service.upload_snapshot(
        user=user,
        proctoring_id=proctoring_id,
        image=image,
        violation_type=violation_type
    )


@router.get("/snapshot/{snapshotId}", status_code=status.HTTP_200_OK)
async def get_snapshot(
    snapshot_id: int = Path(alias="snapshotId"),
    snapshot_service: SnapshotService = Depends(snapshot_service_dependency),
    user: User = Depends(decode_user_token),
) -> SnapshotItemSchema:
    """Получить информацию о конкретном снимке"""
    return await snapshot_service.get_snapshot_by_id(
        user=user,
        snapshot_id=snapshot_id
    )


@router.delete("/snapshot/{snapshotId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_snapshot(
    snapshot_id: int = Path(alias="snapshotId"),
    snapshot_service: SnapshotService = Depends(snapshot_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    """Удалить снимок"""
    await snapshot_service.delete_snapshot(
        user=user,
        snapshot_id=snapshot_id
    )

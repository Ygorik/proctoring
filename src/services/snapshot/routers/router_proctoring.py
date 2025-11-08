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

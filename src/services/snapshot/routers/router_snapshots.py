from fastapi import APIRouter, Depends, Path, UploadFile, Query
from starlette import status

from src.services.authorization.schemas import User
from src.services.snapshot.dependencies import snapshot_service_dependency
from src.services.snapshot.schemas import SnapshotItemSchema
from src.services.snapshot.service import SnapshotService
from src.services.token.service import decode_user_token

router = APIRouter()


@router.post("/snapshot", status_code=status.HTTP_201_CREATED)
async def create_snapshot(
    proctoring_id: int | None = Query(None, alias="proctoringId"),
    image: UploadFile = None,
    violation_type: str | None = Query(None, alias="violationType"),
    snapshot_service: SnapshotService = Depends(snapshot_service_dependency),
    user: User = Depends(decode_user_token),
) -> SnapshotItemSchema:
    """Создать новый снимок для сессии прокторинга"""
    return await snapshot_service.create_snapshot(
        user=user,
        proctoring_id=proctoring_id,
        image=image,
        violation_type=violation_type,
        user_id=user.id
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
        snapshot_id=snapshot_id,
    )


@router.put("/snapshot/{snapshotId}", status_code=status.HTTP_200_OK)
async def update_snapshot(
    snapshot_id: int = Path(alias="snapshotId"),
    proctoring_id: int | None = Query(None, alias="proctoringId"),
    violation_type: str | None = Query(None, alias="violationType"),
    snapshot_service: SnapshotService = Depends(snapshot_service_dependency),
    user: User = Depends(decode_user_token),
) -> SnapshotItemSchema:
    """Обновить информацию о снимке"""
    return await snapshot_service.update_snapshot(
        user=user,
        snapshot_id=snapshot_id,
        proctoring_id=proctoring_id,
        violation_type=violation_type
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

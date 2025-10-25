"""Dependencies для snapshot сервиса"""
from typing import Annotated

from fastapi import Depends

from src.db.base_db_service import Session
from src.services.snapshot.db_service import SnapshotDBService
from src.services.snapshot.service import SnapshotService
from src.services.proctoring.db_service import ProctoringDBService
from src.services.proctoring.dependencies import proctoring_db_service_dependency
from src.services.user.db_service import UserDBService
from src.services.user.dependencies import user_db_service_dependency


async def snapshot_db_service_dependency() -> SnapshotDBService:
    """Dependency для SnapshotDBService"""
    return SnapshotDBService(Session)


async def snapshot_service_dependency(
    snapshot_db_service: SnapshotDBService = Depends(snapshot_db_service_dependency),
    proctoring_db_service: ProctoringDBService = Depends(proctoring_db_service_dependency),
    user_db_service: UserDBService = Depends(user_db_service_dependency),
) -> SnapshotService:
    """Dependency для SnapshotService"""
    return SnapshotService(
        snapshot_db_service=snapshot_db_service,
        proctoring_db_service=proctoring_db_service,
        user_db_service=user_db_service,
    )


SnapshotServiceDep = Annotated[SnapshotService, Depends(snapshot_service_dependency)]

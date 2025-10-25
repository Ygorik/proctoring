"""Dependencies для snapshot сервиса"""
from typing import Annotated

from fastapi import Depends

from src.services.snapshot.db_service import SnapshotDBService
from src.services.snapshot.service import SnapshotService
from src.services.proctoring.db_service import ProctoringDBService
from src.services.user.db_service import UserDBService


def snapshot_db_service_dependency() -> SnapshotDBService:
    """Dependency для SnapshotDBService"""
    return SnapshotDBService()


def snapshot_service_dependency(
    snapshot_db_service: SnapshotDBService = Depends(snapshot_db_service_dependency),
) -> SnapshotService:
    """Dependency для SnapshotService"""
    return SnapshotService(
        snapshot_db_service=snapshot_db_service,
        proctoring_db_service=ProctoringDBService(),
        user_db_service=UserDBService(),
    )


SnapshotServiceDep = Annotated[SnapshotService, Depends(snapshot_service_dependency)]

from fastapi import Depends

from src.db.base_db_service import Session
from src.services.proctoring.db_service import ProctoringDBService
from src.services.proctoring.service import ProctoringService


async def proctoring_db_service_dependency() -> ProctoringDBService:
    return ProctoringDBService(Session)


async def proctoring_service_dependency(
    proctoring_db_service: ProctoringDBService = Depends(proctoring_db_service_dependency),
) -> ProctoringService:
    return ProctoringService(proctoring_db_service=proctoring_db_service)

from fastapi import Depends

from src.db.base_db_service import Session
from src.services.proctoring_result.db_service import ProctoringResultDBService
from src.services.proctoring_result.service import ProctoringResultService


async def proctoring_result_db_service_dependency() -> ProctoringResultDBService:
    return ProctoringResultDBService(Session)


async def proctoring_result_service_dependency(
    proctoring_result_db_service: ProctoringResultDBService = Depends(
        proctoring_result_db_service_dependency
    ),
) -> ProctoringResultService:
    return ProctoringResultService(
        proctoring_result_db_service=proctoring_result_db_service
    )

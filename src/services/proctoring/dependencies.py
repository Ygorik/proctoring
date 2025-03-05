from fastapi import Depends

from src.db.base_db_service import Session
from src.services.proctoring.db_service import ProctoringDBService
from src.services.proctoring.service import ProctoringService
from src.services.subject.db_service import SubjectDBService
from src.services.subject.dependencies import (
    subject_db_service_dependency,
)
from src.services.user.db_service import UserDBService
from src.services.user.dependencies import (
    user_db_service_dependency,
)


async def proctoring_db_service_dependency() -> ProctoringDBService:
    return ProctoringDBService(Session)


async def proctoring_service_dependency(
    proctoring_db_service: ProctoringDBService = Depends(
        proctoring_db_service_dependency
    ),
    user_db_service: UserDBService = Depends(user_db_service_dependency),
    subject_db_service: SubjectDBService = Depends(subject_db_service_dependency),
) -> ProctoringService:
    return ProctoringService(
        proctoring_db_service=proctoring_db_service,
        user_db_service=user_db_service,
        subject_db_service=subject_db_service,
    )

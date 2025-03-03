from fastapi import Depends

from src.db.base_db_service import Session
from src.services.subject.db_service import SubjectDBService
from src.services.subject.service import SubjectService
from src.services.user.dependencies import user_service_dependency
from src.services.user.service import UserService


async def subject_db_service_dependency() -> SubjectDBService:
    return SubjectDBService(Session)


async def subject_service_dependency(
    subject_db_service: SubjectDBService = Depends(subject_db_service_dependency),
    user_service: UserService = Depends(user_service_dependency),
) -> SubjectService:
    return SubjectService(
        subject_db_service=subject_db_service, user_service=user_service
    )

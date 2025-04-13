from fastapi import Depends

from src.db.base_db_service import Session
from src.services.base_.db_service import DBService
from src.services.base_.service import Service


async def db_service_dependency() -> DBService:
    return DBService(Session)


async def service_dependency(
    db_service: DBService = Depends(db_service_dependency),
) -> Service:
    return Service(db_service=db_service)

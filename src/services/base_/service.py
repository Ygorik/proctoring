from src.services.base_.db_service import DBService


class Service:
    def __init__(self, *, db_service: DBService) -> None:
        self.db_service = db_service

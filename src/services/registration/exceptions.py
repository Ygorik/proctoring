from starlette import status

from src.base_schemas import BaseBackendError


class FieldAlreadyUseError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "Данные уже используются",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, message=message, data=data
        )

from starlette import status

from src.base_schemas import BaseBackendError


class SubjectNotFoundError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "Предмет с данным ID не найден.",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, message=message, data=data
        )

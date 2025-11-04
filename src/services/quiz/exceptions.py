from starlette import status

from src.base_schemas import BaseBackendError


class QuizNotFoundError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "Тестирование не найдено.",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, message=message, data=data
        )

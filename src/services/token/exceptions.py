from starlette import status

from src.base_schemas import BaseBackendError


class WrongTokenError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "Невалидный токен",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, message=message, data=data
        )

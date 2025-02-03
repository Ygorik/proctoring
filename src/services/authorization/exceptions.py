from starlette import status

from src.base_schemas import BaseBackendError


class UserNotFoundError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "Пользователь не найден",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, message=message, data=data
        )


class WrongPasswordError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "Неверный пароль",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, message=message, data=data
        )

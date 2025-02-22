from starlette import status

from src.base_schemas import BaseBackendError


class RoleNotFoundError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "Роль не найдена.",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, message=message, data=data
        )


class UserHaveRoleError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "Нельзя удалить роль, которая есть у пользователя.",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, message=message, data=data
        )


class UserCanNotReadError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "У данного пользователя нет прав чтения.",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, message=message, data=data
        )


class UserCanNotCreateError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "У данного пользователя нет прав создания.",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, message=message, data=data
        )


class UserCanNotUpdateError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "У данного пользователя нет прав обновления.",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, message=message, data=data
        )


class UserCanNotDeleteError(BaseBackendError):
    def __init__(
        self,
        message: str | None = "У данного пользователя нет прав удаления.",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, message=message, data=data
        )

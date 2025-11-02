from starlette import status

from src.base_schemas import BaseBackendError


class SnapshotNotFoundError(BaseBackendError):
    """Снимок не найден"""
    
    def __init__(
        self,
        message: str | None = "Снимок не найден",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            message=message, 
            data=data
        )


class SnapshotUploadError(BaseBackendError):
    """Ошибка при загрузке снимка"""
    
    def __init__(
        self,
        message: str | None = "Ошибка при загрузке снимка в хранилище",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            message=message, 
            data=data
        )


class SnapshotDownloadError(BaseBackendError):
    """Ошибка при скачивании снимка"""
    
    def __init__(
        self,
        message: str | None = "Ошибка при скачивании снимка из хранилища",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            message=message, 
            data=data
        )


class InvalidImageFormatError(BaseBackendError):
    """Неверный формат изображения"""
    
    def __init__(
        self,
        message: str | None = "Неверный формат изображения. Поддерживаются только изображения (image/*)",
        data: list | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            message=message, 
            data=data
        )

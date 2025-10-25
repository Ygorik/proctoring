"""Исключения для сервиса снимков"""


class SnapshotNotFoundError(Exception):
    """Снимок не найден"""
    pass


class SnapshotUploadError(Exception):
    """Ошибка при загрузке снимка"""
    pass


class SnapshotDownloadError(Exception):
    """Ошибка при скачивании снимка"""
    pass


class InvalidImageFormatError(Exception):
    """Неверный формат изображения"""
    pass

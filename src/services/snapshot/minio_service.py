"""Сервис для работы с MinIO хранилищем"""
import io
from datetime import datetime
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from src.config import settings


class MinIOService:
    """Сервис для взаимодействия с MinIO объектным хранилищем"""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Создает bucket если он не существует"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Error checking/creating bucket: {e}")
    
    def generate_object_key(
        self, 
        user_id: int, 
        proctoring_id: int,
        timestamp: datetime,
        violation_type: str | None = None
    ) -> str:
        """
        Генерирует ключ объекта по шаблону:
        user_{user_id}/{YYYY-MM-DD}/{timestamp}_{type}.jpg
        """
        date_str = timestamp.strftime("%Y-%m-%d")
        timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        type_suffix = f"_{violation_type}" if violation_type else "_normal"
        
        return f"user_{user_id}/{date_str}/{timestamp_str}{type_suffix}.jpg"
    
    def upload_snapshot(
        self,
        file_data: bytes | BinaryIO,
        object_key: str,
        content_type: str = "image/jpeg"
    ) -> tuple[str, int]:
        """
        Загружает снимок в MinIO
        
        Returns:
            tuple: (object_key, file_size)
        """
        try:
            # Если передан bytes, конвертируем в BytesIO
            if isinstance(file_data, bytes):
                file_stream = io.BytesIO(file_data)
                file_size = len(file_data)
            else:
                file_stream = file_data
                # Получаем размер файла
                file_stream.seek(0, 2)  # Перемещаемся в конец
                file_size = file_stream.tell()
                file_stream.seek(0)  # Возвращаемся в начало
            
            # Загружаем файл
            self.client.put_object(
                self.bucket_name,
                object_key,
                file_stream,
                length=file_size,
                content_type=content_type
            )
            
            return object_key, file_size
            
        except S3Error as e:
            raise Exception(f"Failed to upload snapshot: {e}")
    
    def download_snapshot(self, object_key: str) -> bytes:
        """
        Скачивает снимок из MinIO
        
        Returns:
            bytes: содержимое файла
        """
        try:
            response = self.client.get_object(self.bucket_name, object_key)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise Exception(f"Failed to download snapshot: {e}")
    
    def delete_snapshot(self, object_key: str) -> None:
        """Удаляет снимок из MinIO"""
        try:
            self.client.remove_object(self.bucket_name, object_key)
        except S3Error as e:
            raise Exception(f"Failed to delete snapshot: {e}")
    
    def list_snapshots(self, prefix: str) -> list[str]:
        """
        Получает список объектов по префиксу
        
        Args:
            prefix: префикс для поиска (например, "user_123/2025-10-25/")
        
        Returns:
            list: список ключей объектов
        """
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=True
            )
            return [obj.object_name for obj in objects]
        except S3Error as e:
            raise Exception(f"Failed to list snapshots: {e}")


# Глобальный экземпляр сервиса
minio_service = MinIOService()

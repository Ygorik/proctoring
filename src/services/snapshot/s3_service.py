"""Асинхронный сервис для работы с S3-совместимым хранилищем через aioboto3"""
import io
from datetime import datetime
from typing import BinaryIO
from contextlib import asynccontextmanager

import aioboto3
from botocore.exceptions import ClientError

from src.config import settings


class S3Service:
    """Асинхронный сервис для взаимодействия с S3-совместимым объектным хранилищем (MinIO)"""
    
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.endpoint_url = f"{'https' if settings.MINIO_SECURE else 'http'}://{settings.MINIO_ENDPOINT}"
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self._bucket_initialized = False
    
    @asynccontextmanager
    async def _get_client(self):
        """Контекстный менеджер для получения S3 клиента"""
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as client:
            yield client
    
    async def _ensure_bucket_exists(self) -> None:
        """Создает bucket если он не существует"""
        if self._bucket_initialized:
            return
            
        try:
            async with self._get_client() as client:
                try:
                    await client.head_bucket(Bucket=self.bucket_name)
                    self._bucket_initialized = True
                except ClientError as e:
                    # Если bucket не найден, создаем его
                    error_code = e.response.get('Error', {}).get('Code', '')
                    if error_code == '404':
                        await client.create_bucket(Bucket=self.bucket_name)
                        self._bucket_initialized = True
                        print(f"Created bucket: {self.bucket_name}")
                    else:
                        raise
        except Exception as e:
            print(f"Error checking/creating bucket: {e}")
            raise
    
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
        timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S-%f")[:23]  # Включаем миллисекунды
        type_suffix = f"_{violation_type}" if violation_type else "_normal"
        
        return f"user_{user_id}/{date_str}/{timestamp_str}{type_suffix}.jpg"
    
    async def upload_snapshot(
        self,
        file_data: bytes | BinaryIO,
        object_key: str,
        content_type: str = "image/jpeg"
    ) -> tuple[str, int]:
        """
        Асинхронно загружает снимок в S3
        
        Args:
            file_data: Данные файла (bytes или file-like объект)
            object_key: Ключ объекта в S3
            content_type: MIME-тип содержимого
        
        Returns:
            tuple: (object_key, file_size)
        """
        await self._ensure_bucket_exists()
        
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
            
            # Загружаем файл асинхронно
            async with self._get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=file_stream,
                    ContentType=content_type,
                    ContentLength=file_size
                )
            
            return object_key, file_size
            
        except ClientError as e:
            raise Exception(f"Failed to upload snapshot: {e}")
    
    async def download_snapshot(self, object_key: str) -> bytes:
        """
        Асинхронно скачивает снимок из S3
        
        Args:
            object_key: Ключ объекта в S3
        
        Returns:
            bytes: содержимое файла
        """
        await self._ensure_bucket_exists()
        
        try:
            async with self._get_client() as client:
                response = await client.get_object(
                    Bucket=self.bucket_name,
                    Key=object_key
                )
                # Читаем данные из StreamingBody
                async with response['Body'] as stream:
                    data = await stream.read()
                return data
        except ClientError as e:
            raise Exception(f"Failed to download snapshot: {e}")
    
    async def delete_snapshot(self, object_key: str) -> None:
        """
        Асинхронно удаляет снимок из S3
        
        Args:
            object_key: Ключ объекта в S3
        """
        await self._ensure_bucket_exists()
        
        try:
            async with self._get_client() as client:
                await client.delete_object(
                    Bucket=self.bucket_name,
                    Key=object_key
                )
        except ClientError as e:
            raise Exception(f"Failed to delete snapshot: {e}")
    
    async def list_snapshots(self, prefix: str) -> list[str]:
        """
        Асинхронно получает список объектов по префиксу
        
        Args:
            prefix: префикс для поиска (например, "user_123/2025-10-25/")
        
        Returns:
            list: список ключей объектов
        """
        await self._ensure_bucket_exists()
        
        try:
            object_keys = []
            async with self._get_client() as client:
                paginator = client.get_paginator('list_objects_v2')
                async for page in paginator.paginate(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                ):
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            object_keys.append(obj['Key'])
            
            return object_keys
        except ClientError as e:
            raise Exception(f"Failed to list snapshots: {e}")
    
    async def get_object_metadata(self, object_key: str) -> dict:
        """
        Асинхронно получает метаданные объекта
        
        Args:
            object_key: Ключ объекта в S3
        
        Returns:
            dict: метаданные объекта
        """
        await self._ensure_bucket_exists()
        
        try:
            async with self._get_client() as client:
                response = await client.head_object(
                    Bucket=self.bucket_name,
                    Key=object_key
                )
                return {
                    'content_type': response.get('ContentType'),
                    'content_length': response.get('ContentLength'),
                    'last_modified': response.get('LastModified'),
                    'metadata': response.get('Metadata', {})
                }
        except ClientError as e:
            raise Exception(f"Failed to get object metadata: {e}")


# Глобальный экземпляр сервиса
s3_service = S3Service()

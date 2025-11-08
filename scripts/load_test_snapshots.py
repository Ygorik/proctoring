#!/usr/bin/env python3
"""
Скрипт для загрузки тестовых фотографий (snapshots) в MinIO и БД

Использование:
    python scripts/load_test_snapshots.py                # загрузить случайные + из test_photos/
    python scripts/load_test_snapshots.py --only-dir     # загрузить только из test_photos/
    python scripts/load_test_snapshots.py --clear        # удалить все тестовые фотографии
    
    или через make:
    make load-test-snapshots                             # загрузить все
    make load-test-snapshots-from-dir                    # только из test_photos/
    make clear-test-snapshots                            # удалить
"""
import asyncio
import io
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.services.snapshot.s3_service import s3_service
from src.utils.violation_types import get_violation_name


def generate_test_image(
    text: str, 
    width: int = 640, 
    height: int = 480, 
    color: tuple = (100, 150, 200)
) -> bytes:
    """
    Генерирует тестовое изображение с текстом
    
    Args:
        text: Текст на изображении
        width: Ширина изображения
        height: Высота изображения
        color: Цвет фона (RGB)
    
    Returns:
        bytes: Изображение в формате JPEG
    """
    # Создаем изображение
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)
    
    # Добавляем текст
    try:
        # Пытаемся использовать системный шрифт
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        # Если не получилось, используем дефолтный
        font = ImageFont.load_default()
    
    # Получаем размер текста для центрирования
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Рисуем текст
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Добавляем временную метку
    timestamp_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10, height - 30), timestamp_text, fill=(255, 255, 255))
    
    # Конвертируем в bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=85)
    img_buffer.seek(0)
    
    return img_buffer.getvalue()


def parse_filename(filename: str) -> tuple[datetime | None, str | None]:
    """
    Парсит имя файла в формате: 2025-10-30_12-27-19_looking_away.jpg
    
    Args:
        filename: Имя файла
        
    Returns:
        tuple: (timestamp, violation_type) или (None, None) если не удалось распарсить
    """
    # Паттерн: YYYY-MM-DD_HH-MM-SS_violation_type.jpg
    pattern = r'^(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})_(.+)\.jpe?g$'
    match = re.match(pattern, filename, re.IGNORECASE)
    
    if not match:
        return None, None
    
    year, month, day, hour, minute, second, violation_type = match.groups()
    
    try:
        timestamp = datetime(
            int(year), int(month), int(day),
            int(hour), int(minute), int(second)
        )
        # Если violation_type = "normal" или "ok", то нарушения нет
        if violation_type.lower() in ['normal', 'ok', 'none']:
            violation_type = None
        
        return timestamp, violation_type
    except ValueError:
        return None, None


async def load_snapshots_from_directory():
    """Загружает фотографии из директории test_photos/ и связывает их с первой сессией прокторинга"""
    
    photos_dir = Path(__file__).parent / "test_photos"
    
    if not photos_dir.exists():
        print(f"❌ Директория {photos_dir} не существует!")
        return
    
    # Получаем все файлы изображений
    image_files = list(photos_dir.glob("*.jpg")) + list(photos_dir.glob("*.jpeg"))
    
    if not image_files:
        print(f"⚠️  В директории {photos_dir} нет файлов изображений (.jpg/.jpeg)")
        return
    
    print(f"📂 Найдено {len(image_files)} файлов в {photos_dir}")
    
    # Создаем подключение к БД
    engine = create_async_engine(settings.db_url, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Получаем первую сессию прокторинга
            result = await session.execute(
                text(
                    """
                    SELECT p.id, p.user_id, u.login, s.name as subject_name
                    FROM proctoring p
                    JOIN "user" u ON p.user_id = u.id
                    JOIN subject s ON p.subject_id = s.id
                    ORDER BY p.id
                    LIMIT 1;
                    """
                )
            )
            proctoring_session = result.fetchone()
            
            if not proctoring_session:
                print("⚠️  Нет доступных сессий прокторинга. Сначала запустите load_test_data.py")
                return
            
            proctoring_id, user_id, login, subject_name = proctoring_session
            print(f"📊 Привязываем фотографии к сессии {proctoring_id} ({login} - {subject_name})")
            
            total_uploaded = 0
            skipped = 0
            
            for image_file in sorted(image_files):
                filename = image_file.name
                
                # Парсим имя файла
                timestamp, violation_type = parse_filename(filename)
                
                if timestamp is None:
                    print(f"  ⚠️  Пропускаем {filename}: неверный формат имени")
                    skipped += 1
                    continue
                
                print(f"  📷 Загружаем {filename}...", end=" ")
                print(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}]", end=" ")
                print(f"[{violation_type or 'normal'}]", end=" ")
                
                # Читаем файл
                try:
                    with open(image_file, 'rb') as f:
                        image_data = f.read()
                except Exception as e:
                    print(f"✗ Ошибка чтения: {e}")
                    skipped += 1
                    continue
                
                # Генерируем ключ для S3
                object_key = s3_service.generate_object_key(
                    user_id=user_id,
                    proctoring_id=proctoring_id,
                    timestamp=timestamp,
                    violation_type=violation_type
                )
                
                # Загружаем в S3 асинхронно
                try:
                    object_key, file_size = await s3_service.upload_snapshot(
                        file_data=image_data,
                        object_key=object_key,
                        content_type="image/jpeg"
                    )
                    print(f"✓ S3", end=" ")
                except Exception as e:
                    print(f"✗ Ошибка S3: {e}")
                    skipped += 1
                    continue
                
                # Сохраняем метаданные в БД
                try:
                    await session.execute(
                        text(
                            """
                            INSERT INTO proctoring_snapshot 
                            (proctoring_id, bucket_name, object_key, violation_type)
                            VALUES 
                            (:proctoring_id, :bucket_name, :object_key, :violation_type)
                            """
                        ),
                        {
                            "proctoring_id": proctoring_id,
                            "bucket_name": s3_service.bucket_name,
                            "object_key": object_key,
                            "violation_type": violation_type
                        }
                    )
                    print(f"✓ БД")
                    total_uploaded += 1
                except Exception as e:
                    print(f"✗ Ошибка БД: {e}")
                    skipped += 1
                    continue
            
            await session.commit()
            
            print(f"\n✅ Загрузка завершена!")
            print(f"   - Загружено: {total_uploaded}")
            print(f"   - Пропущено: {skipped}")
            print(f"   - Bucket S3: {s3_service.bucket_name}")
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке фотографий: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


async def load_test_snapshots():
    """Загружает тестовые фотографии для сессий прокторинга"""
    
    # Создаем подключение к БД
    engine = create_async_engine(settings.db_url, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("🔄 Начинаем загрузку тестовых фотографий...")
            
            # Получаем существующие сессии прокторинга
            result = await session.execute(
                text(
                    """
                    SELECT p.id, p.user_id, u.login, s.name as subject_name
                    FROM proctoring p
                    JOIN "user" u ON p.user_id = u.id
                    JOIN subject s ON p.subject_id = s.id
                    LIMIT 3;
                    """
                )
            )
            proctoring_sessions = result.fetchall()
            
            if not proctoring_sessions:
                print("⚠️  Нет доступных сессий прокторинга. Сначала запустите load_test_data.py")
                return
            
            print(f"📊 Найдено {len(proctoring_sessions)} сессий прокторинга")
            
            # Типы нарушений и их цвета
            violation_types = [
                ("looking_away", get_violation_name("looking_away"), (255, 200, 100)),
                ("extra_person", get_violation_name("extra_person"), (255, 100, 100)),
                ("mouth_opening", get_violation_name("mouth_opening"), (200, 150, 255)),
                (None, "Нормально", (100, 200, 150)),
            ]
            
            total_uploaded = 0
            
            # Для каждой сессии загружаем фотографии
            for proctoring_id, user_id, login, subject_name in proctoring_sessions:
                print(f"\n📸 Загружаем фотографии для сессии {proctoring_id} ({login} - {subject_name})...")
                
                # Генерируем 5-8 фотографий для каждой сессии
                num_snapshots = 7
                base_time = datetime.now() - timedelta(hours=2)
                
                for i in range(num_snapshots):
                    # Чередуем нормальные снимки и снимки с нарушениями
                    violation_type, violation_text, color = violation_types[i % len(violation_types)]
                    
                    # Генерируем временную метку
                    snapshot_time = base_time + timedelta(minutes=i * 5 + proctoring_id)
                    
                    # Создаем текст для изображения
                    image_text = f"{login}\n{subject_name}\n{violation_text}"
                    
                    # Генерируем изображение
                    print(f"  📷 Создаем снимок #{i+1}: {violation_text}...", end=" ")
                    image_data = generate_test_image(image_text, color=color)
                    
                    # Генерируем ключ для S3
                    object_key = s3_service.generate_object_key(
                        user_id=user_id,
                        proctoring_id=proctoring_id,
                        timestamp=snapshot_time,
                        violation_type=violation_type
                    )
                    
                    # Загружаем в S3 асинхронно
                    try:
                        object_key, file_size = await s3_service.upload_snapshot(
                            file_data=image_data,
                            object_key=object_key,
                            content_type="image/jpeg"
                        )
                        print(f"✓ S3", end=" ")
                    except Exception as e:
                        print(f"✗ Ошибка S3: {e}")
                        continue
                    
                    # Сохраняем метаданные в БД
                    try:
                        await session.execute(
                            text(
                                """
                                INSERT INTO proctoring_snapshot 
                                (proctoring_id, bucket_name, object_key, violation_type)
                                VALUES 
                                (:proctoring_id, :bucket_name, :object_key, :violation_type)
                                """
                            ),
                            {
                                "proctoring_id": proctoring_id,
                                "bucket_name": s3_service.bucket_name,
                                "object_key": object_key,
                                "violation_type": violation_type
                            }
                        )
                        print(f"✓ БД")
                        total_uploaded += 1
                    except Exception as e:
                        print(f"✗ Ошибка БД: {e}")
                        continue
            
            await session.commit()
            
            print(f"\n✅ Успешно загружено {total_uploaded} тестовых фотографий!")
            print(f"\n📊 Статистика:")
            print(f"   - Сессий прокторинга: {len(proctoring_sessions)}")
            print(f"   - Фотографий на сессию: ~{num_snapshots}")
            print(f"   - Bucket S3: {s3_service.bucket_name}")
            print(f"\n💡 Теперь можно сгенерировать PDF-отчет:")
            print(f"   curl -H 'Authorization: Bearer TOKEN' http://localhost:8000/api/v1/proctoring/1/report -o report.pdf")
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке фотографий: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


async def clear_test_snapshots():
    """Удаляет все тестовые фотографии из MinIO и БД"""
    
    engine = create_async_engine(settings.db_url, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("🔄 Начинаем удаление тестовых фотографий...")
            
            # Получаем все snapshot'ы из БД
            result = await session.execute(
                text("SELECT id, object_key FROM proctoring_snapshot")
            )
            snapshots = result.fetchall()
            
            print(f"📊 Найдено {len(snapshots)} фотографий для удаления")
            
            deleted_from_minio = 0
            deleted_from_db = 0
            
            # Удаляем каждый snapshot
            for snapshot_id, object_key in snapshots:
                # Удаляем из S3 асинхронно
                try:
                    await s3_service.delete_snapshot(object_key)
                    deleted_from_minio += 1
                    print(f"  ✓ Удалено из S3: {object_key}")
                except Exception as e:
                    print(f"  ⚠️  Не удалось удалить из S3: {object_key} ({e})")
            
            # Удаляем все записи из БД
            await session.execute(text("DELETE FROM proctoring_snapshot"))
            await session.commit()
            deleted_from_db = len(snapshots)
            
            print(f"\n✅ Удаление завершено!")
            print(f"   - Из S3: {deleted_from_minio}")
            print(f"   - Из БД: {deleted_from_db}")
            
        except Exception as e:
            print(f"❌ Ошибка при удалении фотографий: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


async def load_all_snapshots():
    """Загружает и случайные фотографии, и фотографии из директории"""
    # Сначала загружаем случайные сгенерированные
    await load_test_snapshots()
    
    print("\n" + "="*60)
    
    # Затем загружаем из директории (если есть файлы)
    photos_dir = Path(__file__).parent / "test_photos"
    if photos_dir.exists():
        image_files = list(photos_dir.glob("*.jpg")) + list(photos_dir.glob("*.jpeg"))
        if image_files:
            await load_snapshots_from_directory()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Управление тестовыми фотографиями")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Удалить тестовые фотографии вместо загрузки"
    )
    parser.add_argument(
        "--only-dir",
        action="store_true",
        help="Загрузить только фотографии из директории test_photos/ (без генерации случайных)"
    )
    
    args = parser.parse_args()
    
    if args.clear:
        asyncio.run(clear_test_snapshots())
    elif args.only_dir:
        asyncio.run(load_snapshots_from_directory())
    else:
        asyncio.run(load_all_snapshots())

#!/usr/bin/env python3
"""
Скрипт для загрузки тестовых данных в базу данных

Использование:
    python scripts/load_test_data.py
    или через make: make load-test-data
"""
import asyncio
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.utils.cryptographer import Cryptographer


async def load_test_data():
    """Загружает тестовые данные в базу"""
    
    # Создаем подключение к БД
    engine = create_async_engine(settings.db_url, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("🔄 Начинаем загрузку тестовых данных...")
            
            # Инициализируем криптографер для паролей
            crypto = Cryptographer(settings.CRYPTO_KEY)
            test_password = crypto.encrypt("Test123!")
            
            # 0. Создаем роль для обычных пользователей
            print("📝 Создаем роль 'user'...")
            await session.execute(
                text(
                    """
                    INSERT INTO role (name, rights_create, rights_read, rights_update, rights_delete) 
                    VALUES ('user', FALSE, TRUE, FALSE, FALSE)
                    ON CONFLICT (name) DO NOTHING;
                    """
                )
            )
            
            # 1. Создаем тестовых пользователей
            print("👤 Создаем тестовых пользователей...")
            await session.execute(
                text(
                    """
                    INSERT INTO "user" (login, hashed_password, full_name, role_id) VALUES
                    ('ivanov', :password, 'Иванов Иван Иванович', 2),
                    ('petrov', :password, 'Петров Петр Петрович', 2),
                    ('sidorova', :password, 'Сидорова Анна Сергеевна', 2),
                    ('kuznetsov', :password, 'Кузнецов Алексей Владимирович', 2),
                    ('smirnova', :password, 'Смирнова Елена Дмитриевна', 2)
                    ON CONFLICT (login) DO NOTHING;
                    """
                ).bindparams(password=test_password)
            )
            
            # 2. Создаем тестовые предметы
            print("📚 Создаем тестовые предметы...")
            await session.execute(
                text(
                    """
                    INSERT INTO subject (name) VALUES
                    ('Математика'),
                    ('Физика'),
                    ('Программирование'),
                    ('История'),
                    ('Английский язык')
                    ON CONFLICT (name) DO NOTHING;
                    """
                )
            )
            
            # 3. Привязываем пользователей к предметам
            print("🔗 Привязываем пользователей к предметам...")
            await session.execute(
                text(
                    """
                    INSERT INTO subject_user (subject_id, user_id) 
                    SELECT s.id, u.id 
                    FROM subject s, "user" u 
                    WHERE u.login IN ('ivanov', 'petrov') AND s.name = 'Математика'
                    
                    UNION ALL
                    
                    SELECT s.id, u.id 
                    FROM subject s, "user" u 
                    WHERE u.login IN ('sidorova', 'kuznetsov') AND s.name = 'Физика'
                    
                    UNION ALL
                    
                    SELECT s.id, u.id 
                    FROM subject s, "user" u 
                    WHERE u.login IN ('smirnova', 'ivanov') AND s.name = 'Программирование'
                    ON CONFLICT DO NOTHING;
                    """
                )
            )
            
            # 4. Создаем типы прокторинга
            print("🎯 Создаем типы прокторинга...")
            await session.execute(
                text(
                    """
                    INSERT INTO proctoring_type (name, absence_person, extra_person, person_substitution, looking_away, mouth_opening, hints_outside) VALUES
                    ('Строгий контроль', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE),
                    ('Стандартный контроль', TRUE, TRUE, TRUE, TRUE, FALSE, FALSE),
                    ('Базовый контроль', TRUE, TRUE, FALSE, FALSE, FALSE, FALSE),
                    ('Минимальный контроль', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE)
                    ON CONFLICT (name) DO NOTHING;
                    """
                )
            )
            
            # 5. Создаем результаты прокторинга
            print("📊 Создаем результаты прокторинга...")
            await session.execute(
                text(
                    """
                    INSERT INTO proctoring_result (detected_absence_person, detected_extra_person, detected_person_substitution, detected_looking_away, detected_mouth_opening, detected_hints_outside) VALUES
                    (FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
                    (FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
                    (FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
                    (FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
                    (TRUE, FALSE, FALSE, FALSE, FALSE, FALSE);
                    """
                )
            )
            
            # 6. Создаем сессии прокторинга
            print("🎥 Создаем сессии прокторинга...")
            
            # Сессия 1: Иванов - Математика
            await session.execute(
                text(
                    """
                    INSERT INTO proctoring (user_id, subject_id, type_id, result_id)
                    SELECT 
                        u.id,
                        s.id,
                        pt.id,
                        pr.id
                    FROM "user" u
                    CROSS JOIN subject s
                    CROSS JOIN proctoring_type pt
                    CROSS JOIN proctoring_result pr
                    WHERE u.login = 'ivanov' 
                      AND s.name = 'Математика' 
                      AND pt.name = 'Строгий контроль'
                      AND pr.id = 1
                    LIMIT 1
                    ON CONFLICT DO NOTHING;
                    """
                )
            )
            
            # Сессия 2: Петров - Математика
            await session.execute(
                text(
                    """
                    INSERT INTO proctoring (user_id, subject_id, type_id, result_id)
                    SELECT 
                        u.id,
                        s.id,
                        pt.id,
                        pr.id
                    FROM "user" u
                    CROSS JOIN subject s
                    CROSS JOIN proctoring_type pt
                    CROSS JOIN proctoring_result pr
                    WHERE u.login = 'petrov' 
                      AND s.name = 'Математика' 
                      AND pt.name = 'Стандартный контроль'
                      AND pr.id = 2
                    LIMIT 1
                    ON CONFLICT DO NOTHING;
                    """
                )
            )
            
            # Сессия 3: Сидорова - Физика
            await session.execute(
                text(
                    """
                    INSERT INTO proctoring (user_id, subject_id, type_id, result_id)
                    SELECT 
                        u.id,
                        s.id,
                        pt.id,
                        pr.id
                    FROM "user" u
                    CROSS JOIN subject s
                    CROSS JOIN proctoring_type pt
                    CROSS JOIN proctoring_result pr
                    WHERE u.login = 'sidorova' 
                      AND s.name = 'Физика' 
                      AND pt.name = 'Стандартный контроль'
                      AND pr.id = 3
                    LIMIT 1
                    ON CONFLICT DO NOTHING;
                    """
                )
            )
            
            await session.commit()
            
            print("✅ Тестовые данные успешно загружены!")
            print("\n📋 Созданные тестовые пользователи:")
            print("   Login: ivanov, petrov, sidorova, kuznetsov, smirnova")
            print("   Password: Test123!")
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке данных: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


async def clear_test_data():
    """Удаляет тестовые данные из базы"""
    
    engine = create_async_engine(settings.db_url, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("🔄 Начинаем удаление тестовых данных...")
            
            # Удаляем в обратном порядке из-за foreign keys
            await session.execute(
                text(
                    """
                    DELETE FROM proctoring 
                    WHERE user_id IN (
                        SELECT id FROM "user" 
                        WHERE login IN ('ivanov', 'petrov', 'sidorova', 'kuznetsov', 'smirnova')
                    );
                    """
                )
            )
            
            await session.execute(
                text("DELETE FROM proctoring_result WHERE id BETWEEN 1 AND 5;")
            )
            
            await session.execute(
                text(
                    """
                    DELETE FROM proctoring_type 
                    WHERE name IN ('Строгий контроль', 'Стандартный контроль', 'Базовый контроль', 'Минимальный контроль');
                    """
                )
            )
            
            await session.execute(
                text(
                    """
                    DELETE FROM subject_user 
                    WHERE subject_id IN (
                        SELECT id FROM subject 
                        WHERE name IN ('Математика', 'Физика', 'Программирование', 'История', 'Английский язык')
                    );
                    """
                )
            )
            
            await session.execute(
                text(
                    """
                    DELETE FROM subject 
                    WHERE name IN ('Математика', 'Физика', 'Программирование', 'История', 'Английский язык');
                    """
                )
            )
            
            await session.execute(
                text(
                    """
                    DELETE FROM "user" 
                    WHERE login IN ('ivanov', 'petrov', 'sidorova', 'kuznetsov', 'smirnova');
                    """
                )
            )
            
            await session.execute(
                text("DELETE FROM role WHERE name='user';")
            )
            
            await session.commit()
            
            print("✅ Тестовые данные успешно удалены!")
            
        except Exception as e:
            print(f"❌ Ошибка при удалении данных: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Управление тестовыми данными")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Удалить тестовые данные вместо загрузки"
    )
    
    args = parser.parse_args()
    
    if args.clear:
        asyncio.run(clear_test_data())
    else:
        asyncio.run(load_test_data())

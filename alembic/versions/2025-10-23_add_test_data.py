"""add_test_data

Revision ID: 3aa09cb474cc
Revises: 0269e16731d6
Create Date: 2025-10-23 14:47:01.476324

"""
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.utils.cryptographer import Cryptographer


# revision identifiers, used by Alembic.
revision: str = '3aa09cb474cc'
down_revision: Union[str, None] = '0269e16731d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Инициализируем криптографер для паролей
    crypto = Cryptographer(os.getenv("CRYPTO_KEY"))
    
    # 0. Создаем роль для обычных пользователей
    op.execute(
        sa.text(
            """
            INSERT INTO role (name, rights_create, rights_read, rights_update, rights_delete) 
            VALUES ('user', FALSE, TRUE, FALSE, FALSE)
            ON CONFLICT DO NOTHING;
            """
        )
    )
    
    # 1. Создаем тестовых пользователей (role_id=2 - обычные пользователи)
    # Пароли: Test123! для всех
    test_password = crypto.encrypt("Test123!")
    
    op.execute(
        sa.text(
            """
            INSERT INTO "user" (login, hashed_password, full_name, role_id) VALUES
            ('ivanov', :password, 'Иванов Иван Иванович', 2),
            ('petrov', :password, 'Петров Петр Петрович', 2),
            ('sidorova', :password, 'Сидорова Анна Сергеевна', 2),
            ('kuznetsov', :password, 'Кузнецов Алексей Владимирович', 2),
            ('smirnova', :password, 'Смирнова Елена Дмитриевна', 2);
            """
        ).bindparams(password=test_password)
    )
    
    # 2. Создаем тестовые предметы
    op.execute(
        sa.text(
            """
            INSERT INTO subject (name) VALUES
            ('Математика'),
            ('Физика'),
            ('Программирование'),
            ('История'),
            ('Английский язык');
            """
        )
    )
    
    # 3. Привязываем пользователей к предметам
    op.execute(
        sa.text(
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
            WHERE u.login IN ('smirnova', 'ivanov') AND s.name = 'Программирование';
            """
        )
    )
    
    # 4. Создаем типы прокторинга
    op.execute(
        sa.text(
            """
            INSERT INTO proctoring_type (name, absence_person, extra_person, person_substitution, looking_away, mouth_opening, hints_outside) VALUES
            ('Строгий контроль', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE),
            ('Стандартный контроль', TRUE, TRUE, TRUE, TRUE, FALSE, FALSE),
            ('Базовый контроль', TRUE, TRUE, FALSE, FALSE, FALSE, FALSE),
            ('Минимальный контроль', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE);
            """
        )
    )
    
    # 5. Создаем результаты прокторинга
    op.execute(
        sa.text(
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
    op.execute(
        sa.text(
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
            LIMIT 1;
            """
        )
    )
    
    op.execute(
        sa.text(
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
            LIMIT 1;
            """
        )
    )
    
    op.execute(
        sa.text(
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
            LIMIT 1;
            """
        )
    )


def downgrade() -> None:
    # Удаляем тестовые данные в обратном порядке (из-за foreign keys)
    op.execute(sa.text("DELETE FROM proctoring WHERE user_id IN (SELECT id FROM \"user\" WHERE login IN ('ivanov', 'petrov', 'sidorova', 'kuznetsov', 'smirnova'));"))
    op.execute(sa.text("DELETE FROM proctoring_result WHERE id BETWEEN 1 AND 5;"))
    op.execute(sa.text("DELETE FROM proctoring_type WHERE name IN ('Строгий контроль', 'Стандартный контроль', 'Базовый контроль', 'Минимальный контроль');"))
    op.execute(sa.text("DELETE FROM subject_user WHERE subject_id IN (SELECT id FROM subject WHERE name IN ('Математика', 'Физика', 'Программирование', 'История', 'Английский язык'));"))
    op.execute(sa.text("DELETE FROM subject WHERE name IN ('Математика', 'Физика', 'Программирование', 'История', 'Английский язык');"))
    op.execute(sa.text("DELETE FROM \"user\" WHERE login IN ('ivanov', 'petrov', 'sidorova', 'kuznetsov', 'smirnova');"))
    op.execute(sa.text("DELETE FROM role WHERE name='user';"))

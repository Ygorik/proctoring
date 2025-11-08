"""Утилиты для работы с типами нарушений прокторинга."""

from typing import Dict

# Маппинг технических названий нарушений на человекочитаемые (русский язык)
VIOLATION_TYPE_NAMES: Dict[str, str] = {
    "absence_person": "Отсутствие человека",
    "extra_person": "Посторонний человек",
    "person_substitution": "Подмена личности",
    "looking_away": "Отвод взгляда",
    "mouth_opening": "Открытие рта",
    "hints_outside": "Подсказки извне",
}


def get_violation_name(violation_type: str | None) -> str:
    """
    Возвращает человекочитаемое название нарушения.
    
    Args:
        violation_type: Технический идентификатор нарушения
        
    Returns:
        Русское название нарушения или исходное значение, если не найдено
    """
    if violation_type is None:
        return "Нарушений нет"
    return VIOLATION_TYPE_NAMES.get(violation_type, violation_type)

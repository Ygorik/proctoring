import os
import io
import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO, Iterable

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

from sqlalchemy import select, desc, case, literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.proctoring_model import ProctoringDB
from src.services.snapshot.s3_service import s3_service
from src.utils.violation_types import get_violation_name


@dataclass(frozen=True)
class _Layout:
    margin: int = 72
    img_w: float = 4.5 * inch
    img_h: float = 3.4 * inch
    id_photo_w: float = 2.2 * inch  # Увеличенная идентификационная фотография
    id_photo_h: float = 2.8 * inch
    gap_sm: float = 0.15 * inch
    gap_md: float = 0.3 * inch
    gap_lg: float = 0.5 * inch
    gap_xl: float = 0.7 * inch
    s3_concurrency: int = 8  # критично: держим разумный лимит параллельных скачиваний


class PDFReportService:
    """Сервис формирования лёгкого и быстрого фоторапорта по прокторингу."""

    def __init__(self) -> None:
        self._register_fonts()
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self.ui = _Layout()

    def _register_fonts(self) -> None:
        """Регистрирует гарнитуру с кириллицей."""
        candidates_regular = [
            os.getenv("REPORTLAB_FONT_DEJAVU_SANS"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/local/share/fonts/DejaVuSans.ttf",
            "resources/fonts/DejaVuSans.ttf",
            "fonts/DejaVuSans.ttf",
        ]
        candidates_bold = [
            os.getenv("REPORTLAB_FONT_DEJAVU_SANS_BOLD"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/local/share/fonts/DejaVuSans-Bold.ttf",
            "resources/fonts/DejaVuSans-Bold.ttf",
            "fonts/DejaVuSans-Bold.ttf",
        ]
        regular = next((p for p in candidates_regular if p and os.path.exists(p)), None)
        bold = next((p for p in candidates_bold if p and os.path.exists(p)), None)
        if not regular or not bold:
            raise RuntimeError("Нет файлов DejaVuSans*.ttf — добавьте их или укажите пути переменными окружения.")
        pdfmetrics.registerFont(TTFont("DejaVuSans", regular))
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold))
        registerFontFamily("DejaVuSans", normal="DejaVuSans", bold="DejaVuSans-Bold", italic="DejaVuSans", boldItalic="DejaVuSans-Bold")

    def _setup_styles(self) -> None:
        """Готовит минимальный набор стилей для повторного использования."""
        # Цветовая палитра: строгий корпоративный стиль
        primary_dark = colors.HexColor("#1A1A2E")  # Темно-синий для заголовков
        secondary_dark = colors.HexColor("#16213E")  # Еще темнее для основного текста
        accent_blue = colors.HexColor("#0F4C75")  # Акцентный синий
        light_gray = colors.HexColor("#53565A")  # Серый для вторичного текста
        
        self.styles.add(
            ParagraphStyle(
                name="TitleX",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=primary_dark,
                spaceAfter=8,
                spaceBefore=0,
                alignment=TA_CENTER,
                fontName="DejaVuSans-Bold",
                leading=28,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SubtitleX",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=light_gray,
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName="DejaVuSans",
                leading=14,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="H2X",
                parent=self.styles["Heading2"],
                fontSize=14,
                textColor=accent_blue,
                spaceBefore=16,
                spaceAfter=10,
                fontName="DejaVuSans-Bold",
                leading=17,
                borderWidth=0,
                borderPadding=0,
                borderColor=None,
                leftIndent=0,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BodyX",
                parent=self.styles["BodyText"],
                fontSize=10,
                leading=13,
                textColor=secondary_dark,
                spaceAfter=6,
                fontName="DejaVuSans",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CaptionX",
                parent=self.styles["BodyText"],
                fontSize=9,
                leading=11,
                spaceAfter=4,
                fontName="DejaVuSans",
                textColor=light_gray,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="LabelX",
                parent=self.styles["BodyText"],
                fontSize=10,
                textColor=light_gray,
                fontName="DejaVuSans-Bold",
                leading=13,
            )
        )

    async def generate_report(self, proctoring_id: int, session: AsyncSession) -> BinaryIO:
        """Формирует PDF-отчёт: заголовок, краткая сводка и фотосекция."""
        data = await self._get_proctoring_data(proctoring_id, session)
        if not data:
            raise ValueError(f"Proctoring session {proctoring_id} not found")

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            rightMargin=self.ui.margin,
            leftMargin=self.ui.margin,
            topMargin=self.ui.margin,
            bottomMargin=self.ui.margin,
            title=f"Proctoring #{proctoring_id}",
            author="Proctoring System",
        )

        story: list = []
        story.extend(self._header(data))
        story.extend(await self._session_block(data))
        story.extend(self._stats_block(data))
        story.extend(await self._snapshots_block(data))

        doc.build(story, onFirstPage=self._page_decor, onLaterPages=self._page_decor)
        buf.seek(0)
        return buf

    async def _get_proctoring_data(self, proctoring_id: int, session: AsyncSession) -> dict | None:
        """Читает из БД с предзагрузкой связанных сущностей и сортировкой снимков."""
        # proctoring + связи
        stmt = (
            select(ProctoringDB)
            .where(ProctoringDB.id == proctoring_id)
            .options(
                selectinload(ProctoringDB.user),
                selectinload(ProctoringDB.subject),
                selectinload(ProctoringDB.proctoring_type),
                selectinload(ProctoringDB.proctoring_result),
            )
        )
        proctoring = (await session.execute(stmt)).scalar_one_or_none()
        if not proctoring:
            return None

        first_id = proctoring.first_photo_id

        from src.db.models.snapshot_model import ProctoringSnapshotDB
        # снимки: "первая" сверху, далее по времени
        # boolean в ORDER BY: CASE быстрее/переносимее
        order_primary_first = desc(
            case((ProctoringSnapshotDB.id == literal(first_id), 1), else_=0)
        )

        snapshots_stmt = (
            select(ProctoringSnapshotDB)
            .where(ProctoringSnapshotDB.proctoring_id == proctoring_id)
            .order_by(order_primary_first, ProctoringSnapshotDB.created_at.asc())
        )

        snaps = list((await session.scalars(snapshots_stmt)).all())

        first_photo = snaps[0] if snaps and first_id and snaps[0].id == first_id else None
        other_snapshots = snaps[1:] if first_photo else snaps

        return {
            "proctoring": proctoring,
            "user": proctoring.user,
            "subject": proctoring.subject,
            "ptype": proctoring.proctoring_type,
            "result": proctoring.proctoring_result,
            "snapshots": other_snapshots,
            "first_photo": first_photo,
        }

    def _header(self, data: dict) -> list:
        """Генерирует верхний блок с заголовком и метаданными."""
        created = data["proctoring"].created_at.strftime("%d.%m.%Y в %H:%M")
        subtitle = f"Дата проведения: {created} • ID сессии: {data['proctoring'].id}"
        
        out: list = [
            Paragraph("ОТЧЁТ О СЕССИИ ПРОКТОРИНГА", self.styles["TitleX"]),
            Paragraph(subtitle, self.styles["SubtitleX"]),
            Spacer(1, self.ui.gap_sm),
        ]
        return out

    async def _session_block(self, data: dict) -> list:
        """Выводит краткие реквизиты сессии с идентификационной фотографией."""
        u = data["user"].login if data["user"] else "Не указано"
        subj = data["subject"].name if data["subject"] else "Не указано"
        
        # TODO: Добавить поля в модель ProctoringDB
        course = "Не указано"  # data["proctoring"].course if hasattr(data["proctoring"], "course") else "Не указано"
        quiz = "Не указано"  # data["proctoring"].quiz if hasattr(data["proctoring"], "quiz") else "Не указано"
        attempt = "Не указано"  # data["proctoring"].attempt if hasattr(data["proctoring"], "attempt") else "Не указано"
        
        # Создаём таблицу с информацией о сессии
        info_data = [
            ["Студент:", u],
            ["Предмет:", subj],
            ["Курс:", course],
            ["Тест/Экзамен:", quiz],
            ["Попытка:", attempt],
        ]
        
        info_table = Table(
            info_data,
            colWidths=[1.4 * inch, 3.0 * inch],
            hAlign="LEFT",
        )
        info_table.setStyle(
            TableStyle([
                ("FONT", (0, 0), (0, -1), "DejaVuSans-Bold", 10),
                ("FONT", (1, 0), (1, -1), "DejaVuSans", 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#53565A")),
                ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#16213E")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        
        result = [
            Paragraph("ИНФОРМАЦИЯ О СЕССИИ", self.styles["H2X"]),
            Spacer(1, self.ui.gap_sm),
        ]
        
        # Добавляем идентификационную фотографию, если она есть
        first_photo = data.get("first_photo")
        if first_photo:
            try:
                photo_bytes = await s3_service.download_snapshot(first_photo.object_key)
                if photo_bytes:
                    # Создаём идентификационную фотографию
                    photo_img = Image(io.BytesIO(photo_bytes))
                    photo_w, photo_h = self.ui.id_photo_w, self.ui.id_photo_h
                    aspect = (photo_img.imageHeight or 1) / (photo_img.imageWidth or 1)
                    if aspect > photo_h / photo_w:
                        photo_img.drawHeight = photo_h
                        photo_img.drawWidth = photo_h / aspect
                    else:
                        photo_img.drawWidth = photo_w
                        photo_img.drawHeight = photo_w * aspect
                    
                    # Подпись под фотографией
                    photo_caption = Paragraph(
                        "<b>ИДЕНТИФИКАЦИОННАЯ<br/>ФОТОГРАФИЯ</b>",
                        self.styles["CaptionX"]
                    )
                    
                    # Контейнер для фото с подписью
                    photo_container = Table(
                        [[photo_img], [photo_caption]],
                        colWidths=[self.ui.id_photo_w],
                    )
                    photo_container.setStyle(
                        TableStyle([
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("VALIGN", (0, 0), (0, 0), "TOP"),
                            ("BOX", (0, 0), (0, 0), 2, colors.HexColor("#0F4C75")),
                            ("TOPPADDING", (0, 0), (0, 0), 6),
                            ("BOTTOMPADDING", (0, 0), (0, 0), 6),
                            ("LEFTPADDING", (0, 0), (0, 0), 6),
                            ("RIGHTPADDING", (0, 0), (0, 0), 6),
                            ("TOPPADDING", (0, 1), (0, 1), 8),
                            ("BOTTOMPADDING", (0, 1), (0, 1), 0),
                        ])
                    )
                    
                    # Объединяем фото и информацию
                    combined_table = Table(
                        [[photo_container, info_table]],
                        colWidths=[self.ui.id_photo_w + 0.3 * inch, 4.4 * inch],
                        hAlign="LEFT",
                    )
                    combined_table.setStyle(
                        TableStyle([
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (0, 0), 16),
                        ])
                    )
                    result.append(combined_table)
                else:
                    result.append(info_table)
            except Exception:
                # Если не удалось загрузить фото, просто показываем таблицу
                result.append(info_table)
        else:
            result.append(info_table)
        
        result.append(Spacer(1, self.ui.gap_lg))
        return result

    def _stats_block(self, data: dict) -> list:
        """Сводит флаги нарушений и счётчики снимков в профессиональной таблице."""
        r = data["result"]
        snaps = data["snapshots"]
        first_photo = data.get("first_photo")
        
        # Если first_photo есть, она не входит в snapshots, добавляем к общему счету
        total = len(snaps) + (1 if first_photo else 0)
        viol_cnt = sum(1 for s in snaps if s.violation_type is not None)
        
        # Формируем список обнаруженных нарушений
        violations = []
        
        if getattr(r, "detected_absence_person", False):
            violations.append([get_violation_name("absence_person"), "✓"])
        if getattr(r, "detected_extra_person", False):
            violations.append([get_violation_name("extra_person"), "✓"])
        if getattr(r, "detected_person_substitution", False):
            violations.append([get_violation_name("person_substitution"), "✓"])
        if getattr(r, "detected_looking_away", False):
            violations.append([get_violation_name("looking_away"), "✓"])
        if getattr(r, "detected_mouth_opening", False):
            violations.append([get_violation_name("mouth_opening"), "✓"])
        if getattr(r, "detected_hints_outside", False):
            violations.append([get_violation_name("hints_outside"), "✓"])
        
        # Проверяем, были ли нарушения (по флагам результата или по реальному количеству снимков)
        has_violations = len(violations) > 0 or viol_cnt > 0
        
        # Запоминаем позицию строки "Нарушений не обнаружено" (она будет перед пустой строкой)
        no_violations_row = len(violations)
        
        # Добавляем строку "Нарушений не обнаружено"
        if has_violations:
            # Если есть нарушения - с прочерком
            violations.append(["Нарушений не обнаружено", "—"])
        else:
            # Если нарушений нет - с галочкой
            violations.append(["Нарушений не обнаружено", "✓"])
        
        # Добавляем разделитель и статистику
        violations.append(["", ""])
        
        violations.append(["Всего сделано снимков", str(total)])
        violations.append(["Снимков с нарушениями", str(viol_cnt)])
        violations.append(["Процент чистых снимков", f"{round((total - viol_cnt) / total * 100) if total > 0 else 0}%"])
        
        table = Table(violations, colWidths=[4.5 * inch, 1.3 * inch])
        
        # Базовые стили
        styles = [
            # Заголовки нарушений
            ("FONT", (0, 0), (0, -4), "DejaVuSans", 10),
            ("FONT", (1, 0), (1, -4), "DejaVuSans-Bold", 11),
            # Статистика внизу
            ("FONT", (0, -3), (0, -1), "DejaVuSans-Bold", 10),
            ("FONT", (1, -3), (1, -1), "DejaVuSans-Bold", 11),
            # Цвета по умолчанию
            ("TEXTCOLOR", (0, 0), (-1, -4), colors.HexColor("#16213E")),
            ("TEXTCOLOR", (1, 0), (1, no_violations_row - 1), colors.HexColor("#E74C3C")),  # Красный для галочек нарушений
            ("TEXTCOLOR", (0, -3), (-1, -1), colors.HexColor("#0F4C75")),  # Синий для статистики
            # Границы
            ("LINEABOVE", (0, -3), (-1, -3), 1.5, colors.HexColor("#0F4C75")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E8E8E8")),
            # Выравнивание
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            # Padding
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            # Фон для статистики
            ("BACKGROUND", (0, -3), (-1, -1), colors.HexColor("#F8F9FA")),
        ]
        
        # Цвет для строки "Нарушений не обнаружено"
        if has_violations:
            # Если есть нарушения - прочерк красный
            styles.append(("TEXTCOLOR", (1, no_violations_row), (1, no_violations_row), colors.HexColor("#E74C3C")))
        else:
            # Если нарушений нет - галочка зеленая
            styles.append(("TEXTCOLOR", (1, no_violations_row), (1, no_violations_row), colors.HexColor("#27AE60")))
        
        table.setStyle(TableStyle(styles))
        
        return [
            Paragraph("РЕЗУЛЬТАТЫ ПРОВЕРКИ", self.styles["H2X"]),
            Spacer(1, self.ui.gap_sm),
            table,
            Spacer(1, self.ui.gap_xl),
        ]

    async def _snapshots_block(self, data: dict) -> list:
        """Готовит фотосессию с параллельной загрузкой и профессиональным оформлением."""
        snaps = data["snapshots"]
        if not snaps:
            return [
                Paragraph("ЗАФИКСИРОВАННЫЕ СНИМКИ", self.styles["H2X"]),
                Spacer(1, self.ui.gap_sm),
                Paragraph("Снимки отсутствуют", self.styles["BodyX"])
            ]

        images = await self._download_images([s.object_key for s in snaps])

        out: list = [
            Paragraph("ЗАФИКСИРОВАННЫЕ СНИМКИ", self.styles["H2X"]),
            Spacer(1, self.ui.gap_sm),
        ]
        
        for idx, (snap, img_bytes) in enumerate(zip(snaps, images), 1):
            if img_bytes is None:
                out.append(
                    Paragraph(
                        f"<font color='#E74C3C'><b>Снимок #{idx}:</b> Не удалось загрузить изображение</font>",
                        self.styles["BodyX"]
                    )
                )
                out.append(Spacer(1, self.ui.gap_sm))
                continue

            box_w, box_h = self.ui.img_w, self.ui.img_h
            img = Image(io.BytesIO(img_bytes))
            aspect = (img.imageHeight or 1) / (img.imageWidth or 1)
            if aspect > box_h / box_w:
                img.drawHeight = box_h
                img.drawWidth = box_h / aspect
            else:
                img.drawWidth = box_w
                img.drawHeight = box_w * aspect

            # Форматируем время
            ts = snap.created_at.strftime("%d.%m.%Y %H:%M:%S") if snap.created_at else "Неизвестно"
            
            # Заголовок с номером и временем
            header_text = f"<b>Снимок #{idx}</b> — {ts}"
            header = Paragraph(header_text, self.styles["BodyX"])
            
            # Статус нарушения
            if snap.violation_type:
                vt_display = get_violation_name(snap.violation_type)
                status = Paragraph(
                    f"<font color='#E74C3C'><b>⚠ Обнаружено нарушение:</b> {vt_display}</font>",
                    self.styles["CaptionX"]
                )
            else:
                status = Paragraph(
                    "<font color='#27AE60'><b>✓ Нарушений не обнаружено</b></font>",
                    self.styles["CaptionX"]
                )
            
            # Группируем снимок с рамкой
            snapshot_table = Table(
                [[header], [img], [status]],
                colWidths=[box_w],
            )
            snapshot_table.setStyle(
                TableStyle([
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E8E8E8")),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ])
            )
            
            out.append(KeepTogether([snapshot_table, Spacer(1, self.ui.gap_md)]))
            
            # Разрыв страницы после каждых двух снимков
            if idx % 2 == 0 and idx < len(snaps):
                out.append(PageBreak())

        return out

    async def _download_images(self, keys: Iterable[str]) -> list[bytes | None]:
        """Качает снимки из S3 параллельно с ограничением конкуренции."""
        sem = asyncio.Semaphore(self.ui.s3_concurrency)

        async def _one(k: str) -> bytes | None:
            async with sem:
                try:
                    return await s3_service.download_snapshot(k)
                except Exception:
                    return None

        tasks = [asyncio.create_task(_one(k)) for k in keys]
        return await asyncio.gather(*tasks)

    def _page_decor(self, canvas, doc) -> None:
        """Рисует профессиональный футер с номером страницы и линией."""
        page_width, page_height = doc.pagesize
        
        # Рисуем горизонтальную линию внизу страницы
        canvas.setStrokeColor(colors.HexColor("#0F4C75"))
        canvas.setLineWidth(2)
        canvas.line(
            self.ui.margin,
            self.ui.margin - 30,
            page_width - self.ui.margin,
            self.ui.margin - 30
        )
        
        # Номер страницы справа
        canvas.setFont("DejaVuSans", 9)
        canvas.setFillColor(colors.HexColor("#53565A"))
        page = doc.page
        canvas.drawRightString(
            page_width - self.ui.margin,
            self.ui.margin - 45,
            f"Страница {page}"
        )
        
        # Текст слева (название системы)
        canvas.setFont("DejaVuSans", 8)
        canvas.drawString(
            self.ui.margin,
            self.ui.margin - 45,
            "Система прокторинга | Автоматически сгенерировано"
        )
        
        canvas.setFillColor(colors.black)


# Глобальный экземпляр сервиса
pdf_report_service = PDFReportService()

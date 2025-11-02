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

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.proctoring_model import ProctoringDB
from src.services.snapshot.s3_service import s3_service


@dataclass(frozen=True)
class _Layout:
    margin: int = 64
    img_w: float = 4.8 * inch
    img_h: float = 3.6 * inch
    gap_sm: float = 0.15 * inch
    gap_md: float = 0.3 * inch
    gap_lg: float = 0.5 * inch
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
        self.styles.add(
            ParagraphStyle(
                name="TitleX",
                parent=self.styles["Heading1"],
                fontSize=22,
                textColor=colors.HexColor("#2C3E50"),
                spaceAfter=24,
                alignment=TA_CENTER,
                fontName="DejaVuSans-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="H2X",
                parent=self.styles["Heading2"],
                fontSize=15,
                textColor=colors.HexColor("#34495E"),
                spaceBefore=12,
                spaceAfter=10,
                fontName="DejaVuSans-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BodyX",
                parent=self.styles["BodyText"],
                fontSize=11,
                leading=14,
                textColor=colors.HexColor("#2C3E50"),
                spaceAfter=6,
                fontName="DejaVuSans",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CaptionX",
                parent=self.styles["BodyText"],
                fontSize=10,
                leading=12,
                spaceAfter=6,
                fontName="DejaVuSans",
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
        story.extend(self._session_block(data))
        story.extend(self._stats_block(data))
        story.extend(await self._snapshots_block(data))

        doc.build(story, onFirstPage=self._page_decor, onLaterPages=self._page_decor)
        buf.seek(0)
        return buf

    async def _get_proctoring_data(self, proctoring_id: int, session: AsyncSession) -> dict | None:
        """Читает из БД с предзагрузкой связанных сущностей и сортировкой снимков."""
        stmt = (
            select(ProctoringDB)
            .where(ProctoringDB.id == proctoring_id)
            .options(
                selectinload(ProctoringDB.user),
                selectinload(ProctoringDB.subject),
                selectinload(ProctoringDB.proctoring_type),
                selectinload(ProctoringDB.proctoring_result),
                selectinload(ProctoringDB.snapshots),
            )
        )
        result = await session.execute(stmt)
        proctoring = result.scalar_one_or_none()
        if not proctoring:
            return None
        # Сортируем по created_at (время загрузки снимка)
        snapshots = sorted(proctoring.snapshots, key=lambda x: x.created_at or datetime.min)
        return {
            "proctoring": proctoring,
            "user": proctoring.user,
            "subject": proctoring.subject,
            "ptype": proctoring.proctoring_type,
            "result": proctoring.proctoring_result,
            "snapshots": snapshots,
        }

    def _header(self, data: dict) -> list:
        """Генерирует верхний блок и титульную строку."""
        out: list = [Paragraph("Отчёт о сессии прокторинга", self.styles["TitleX"]), Spacer(1, self.ui.gap_md)]
        return out

    def _session_block(self, data: dict) -> list:
        """Выводит краткие реквизиты сессии в компактной таблице."""
        u = data["user"].login if data["user"] else "Н/Д"
        subj = data["subject"].name if data["subject"] else "Н/Д"
        created = data["proctoring"].created_at.strftime("%Y-%m-%d %H:%M:%S")
        table = Table(
            [["Студент", u], ["Предмет", subj], ["ID сессии", str(data["proctoring"].id)], ["Дата", created]],
            colWidths=[2.1 * inch, 4.1 * inch],
            hAlign="LEFT",
        )
        table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "DejaVuSans", 11),
                    ("FONT", (0, 0), (0, -1), "DejaVuSans-Bold", 11),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2C3E50")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return [Paragraph("Информация о сессии", self.styles["H2X"]), table, Spacer(1, self.ui.gap_md)]

    def _stats_block(self, data: dict) -> list:
        """Сводит флаги нарушений и счётчики снимков."""
        r = data["result"]
        snaps = data["snapshots"]
        total = len(snaps)
        # Считаем снимки с нарушениями (если есть violation_type, значит есть нарушение)
        viol_cnt = sum(1 for s in snaps if s.violation_type is not None)
        rows: list[list[str]] = []
        if getattr(r, "detected_absence_person", False):
            rows.append(["Отсутствие человека", "Да"])
        if getattr(r, "detected_extra_person", False):
            rows.append(["Посторонний", "Да"])
        if getattr(r, "detected_person_substitution", False):
            rows.append(["Подмена личности", "Да"])
        if getattr(r, "detected_looking_away", False):
            rows.append(["Отвод взгляда", "Да"])
        if getattr(r, "detected_mouth_opening", False):
            rows.append(["Разговор", "Да"])
        if getattr(r, "detected_hints_outside", False):
            rows.append(["Подсказки извне", "Да"])
        if not rows:
            rows.append(["Нарушений не обнаружено", "-"])
        rows.extend([["Всего снимков", str(total)], ["Снимков с нарушениями", str(viol_cnt)]])
        table = Table(rows, colWidths=[3.2 * inch, 1.6 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "DejaVuSans", 11),
                    ("FONT", (0, 0), (0, -1), "DejaVuSans-Bold", 11),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2C3E50")),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BDC3C7")),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ]
            )
        )
        return [Paragraph("Статистика нарушений", self.styles["H2X"]), table, Spacer(1, self.ui.gap_lg)]

    async def _snapshots_block(self, data: dict) -> list:
        """Готовит фотосессию с параллельной загрузкой и 2 карточками на страницу."""
        snaps = data["snapshots"]
        if not snaps:
            return [Paragraph("Сделанные снимки", self.styles["H2X"]), Paragraph("Снимки отсутствуют", self.styles["BodyX"])]

        images = await self._download_images([s.object_key for s in snaps])

        out: list = [Paragraph("Сделанные снимки", self.styles["H2X"]), Spacer(1, self.ui.gap_sm)]
        for idx, (snap, img_bytes) in enumerate(zip(snaps, images), 1):
            if img_bytes is None:
                out.append(Paragraph(f"<font color='red'>Снимок #{idx}: не удалось загрузить</font>", self.styles["BodyX"]))
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

            # Используем created_at вместо timestamp
            ts = snap.created_at.strftime("%Y-%m-%d %H:%M:%S") if snap.created_at else "Н/Д"
            # Если есть violation_type, значит это нарушение
            if snap.violation_type:
                vt = snap.violation_type.replace("<", "&lt;").replace(">", "&gt;")
                caption = Paragraph(f"<b>Снимок #{idx}</b> • {ts}<br/><font color='#E74C3C'>Нарушение: {vt}</font>", self.styles["CaptionX"])
            else:
                caption = Paragraph(f"<b>Снимок #{idx}</b> • {ts}<br/><font color='#2ECC71'>Нарушений нет</font>", self.styles["CaptionX"])

            out.append(KeepTogether([caption, Spacer(1, self.ui.gap_sm), img, Spacer(1, self.ui.gap_md)]))
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
        """Рисует номер страницы и «шапку» основания."""
        canvas.setFont("DejaVuSans", 9)
        canvas.setFillGray(0.35)
        page = doc.page
        canvas.drawRightString(doc.pagesize[0] - self.ui.margin, self.ui.margin - 20, f"Стр. {page}")
        canvas.setFillGray(0.0)


# Глобальный экземпляр сервиса
pdf_report_service = PDFReportService()

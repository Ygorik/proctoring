"""Сервис для генерации PDF отчетов по прокторингу"""
import io
from datetime import datetime
from typing import BinaryIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, 
    Paragraph, 
    Spacer, 
    Image, 
    Table, 
    TableStyle, 
    PageBreak
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.proctoring_model import ProctoringDB
from src.db.models.snapshot_model import ProctoringSnapshotDB
from src.services.snapshot.minio_service import minio_service


class PDFReportService:
    """Сервис для генерации PDF отчетов"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Настройка стилей для PDF"""
        # Стиль для заголовка
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Стиль для подзаголовков
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Стиль для обычного текста
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=6,
            fontName='Helvetica'
        ))
    
    async def generate_report(
        self, 
        proctoring_id: int, 
        session: AsyncSession
    ) -> BinaryIO:
        """
        Генерирует PDF отчет по прокторингу
        
        Args:
            proctoring_id: ID сессии прокторинга
            session: Сессия БД
            
        Returns:
            BinaryIO: PDF файл в виде байтового потока
        """
        # Получаем данные из БД
        proctoring_data = await self._get_proctoring_data(proctoring_id, session)
        
        if not proctoring_data:
            raise ValueError(f"Proctoring session {proctoring_id} not found")
        
        # Создаем PDF в памяти
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Собираем содержимое отчета
        story = []
        
        # Заголовок
        story.extend(self._create_header(proctoring_data))
        
        # Информация о сессии
        story.extend(self._create_session_info(proctoring_data))
        
        # Статистика нарушений
        story.extend(self._create_statistics(proctoring_data))
        
        # Фотографии с временными метками
        story.extend(await self._create_snapshots_section(proctoring_data))
        
        # Генерируем PDF
        doc.build(story)
        
        buffer.seek(0)
        return buffer
    
    async def _get_proctoring_data(
        self, 
        proctoring_id: int, 
        session: AsyncSession
    ) -> dict | None:
        """Получает данные прокторинга из БД"""
        stmt = (
            select(ProctoringDB)
            .where(ProctoringDB.id == proctoring_id)
            .options(
                selectinload(ProctoringDB.user),
                selectinload(ProctoringDB.subject),
                selectinload(ProctoringDB.proctoring_type),
                selectinload(ProctoringDB.proctoring_result),
                selectinload(ProctoringDB.snapshots)
            )
        )
        
        result = await session.execute(stmt)
        proctoring = result.scalar_one_or_none()
        
        if not proctoring:
            return None
        
        return {
            'proctoring': proctoring,
            'user': proctoring.user,
            'subject': proctoring.subject,
            'proctoring_type': proctoring.proctoring_type,
            'result': proctoring.proctoring_result,
            'snapshots': sorted(proctoring.snapshots, key=lambda x: x.timestamp)
        }
    
    def _create_header(self, data: dict) -> list:
        """Создает заголовок отчета"""
        elements = []
        
        title = Paragraph(
            "Proctoring Session Report",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_session_info(self, data: dict) -> list:
        """Создает блок с информацией о сессии"""
        elements = []
        
        elements.append(Paragraph("Session Information", self.styles['CustomHeading']))
        
        info_data = [
            ['Student:', data['user'].username if data['user'] else 'N/A'],
            ['Subject:', data['subject'].name if data['subject'] else 'N/A'],
            ['Session ID:', str(data['proctoring'].id)],
            ['Date:', data['proctoring'].created_at.strftime("%Y-%m-%d %H:%M:%S")],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_statistics(self, data: dict) -> list:
        """Создает блок со статистикой нарушений"""
        elements = []
        
        elements.append(Paragraph("Violations Statistics", self.styles['CustomHeading']))
        
        result = data['result']
        violations = []
        
        if result.detected_absence_person:
            violations.append(['Absence of person', 'Yes'])
        if result.detected_extra_person:
            violations.append(['Extra person detected', 'Yes'])
        if result.detected_person_substitution:
            violations.append(['Person substitution', 'Yes'])
        if result.detected_looking_away:
            violations.append(['Looking away', 'Yes'])
        if result.detected_mouth_opening:
            violations.append(['Mouth opening (speaking)', 'Yes'])
        if result.detected_hints_outside:
            violations.append(['Hints from outside', 'Yes'])
        
        if not violations:
            violations.append(['No violations detected', '-'])
        
        # Добавляем статистику по фото
        snapshots = data['snapshots']
        total_snapshots = len(snapshots)
        violation_snapshots = sum(1 for s in snapshots if s.is_violation)
        
        violations.append(['Total snapshots', str(total_snapshots)])
        violations.append(['Violation snapshots', str(violation_snapshots)])
        
        stats_table = Table(violations, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
            ('BACKGROUND', (1, 0), (1, len(violations)-3), colors.HexColor('#E74C3C')),
            ('BACKGROUND', (1, len(violations)-2), (1, -1), colors.HexColor('#ECF0F1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    async def _create_snapshots_section(self, data: dict) -> list:
        """Создает раздел с фотографиями"""
        elements = []
        
        elements.append(Paragraph("Captured Snapshots", self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.2*inch))
        
        snapshots = data['snapshots']
        
        if not snapshots:
            elements.append(Paragraph("No snapshots available", self.styles['CustomBody']))
            return elements
        
        for idx, snapshot in enumerate(snapshots, 1):
            try:
                # Скачиваем изображение из MinIO
                image_data = minio_service.download_snapshot(snapshot.object_key)
                
                # Создаем изображение из байтов
                img_buffer = io.BytesIO(image_data)
                img = Image(img_buffer, width=4*inch, height=3*inch)
                
                # Информация о снимке
                caption_text = f"<b>Snapshot #{idx}</b><br/>"
                caption_text += f"Time: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}<br/>"
                
                if snapshot.is_violation:
                    caption_text += f"<font color='red'>Violation: {snapshot.violation_type or 'Unknown'}</font><br/>"
                    if snapshot.description:
                        caption_text += f"Description: {snapshot.description}<br/>"
                else:
                    caption_text += "<font color='green'>No violation</font><br/>"
                
                caption = Paragraph(caption_text, self.styles['CustomBody'])
                
                elements.append(caption)
                elements.append(Spacer(1, 0.1*inch))
                elements.append(img)
                elements.append(Spacer(1, 0.3*inch))
                
                # Добавляем разрыв страницы после каждых 2 фото
                if idx % 2 == 0 and idx < len(snapshots):
                    elements.append(PageBreak())
                    
            except Exception as e:
                error_text = f"<font color='red'>Failed to load snapshot #{idx}: {str(e)}</font>"
                elements.append(Paragraph(error_text, self.styles['CustomBody']))
                elements.append(Spacer(1, 0.2*inch))
        
        return elements


# Глобальный экземпляр сервиса
pdf_report_service = PDFReportService()

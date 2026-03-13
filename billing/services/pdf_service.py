from dataclasses import dataclass
from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


@dataclass(frozen=True)
class PreviewLineItem:
    description: str
    quantity: int
    unit_price: Decimal

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity


class InvoicePreviewPdfService:
    filename = 'quote-to-paid-invoice-preview.pdf'
    heading_font_name = 'HeiseiKakuGo-W5'
    body_font_name = 'HeiseiMin-W3'

    def build_pdf(self) -> bytes:
        self._register_fonts()

        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontName=self.heading_font_name,
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#111827'),
            spaceAfter=8,
        )
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading3'],
            fontName=self.heading_font_name,
            fontSize=10,
            leading=12,
            textColor=colors.HexColor('#475569'),
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['BodyText'],
            fontName=self.body_font_name,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155'),
        )
        muted_style = ParagraphStyle(
            'Muted',
            parent=styles['BodyText'],
            fontName=self.body_font_name,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#64748b'),
        )

        items = [
            PreviewLineItem('QuoteToPaid 月次業務設計', 1, Decimal('120000')),
            PreviewLineItem('請求催促フロー初期設定', 1, Decimal('48000')),
            PreviewLineItem('ダッシュボード改善作業', 2, Decimal('18000')),
        ]
        subtotal = sum((item.total for item in items), Decimal('0'))
        tax = subtotal * Decimal('0.10')
        total = subtotal + tax

        story = [
            Paragraph('請求書プレビュー', title_style),
            Paragraph('書類番号: INV-2026-0001', muted_style),
            Paragraph('発行日: 2026年03月14日 / 支払期限: 2026年03月31日', muted_style),
            Spacer(1, 10),
        ]

        parties_table = Table(
            [
                [
                    Paragraph('<b>発行元</b>', heading_style),
                    Paragraph('<b>請求先</b>', heading_style),
                ],
                [
                    Paragraph('QuoteToPaid Studio<br/>東京都<br/>owner@example.com', body_style),
                    Paragraph('Tonomura Consulting<br/>経理ご担当者様<br/>billing@example.com', body_style),
                ],
            ],
            colWidths=[82 * mm, 82 * mm],
            hAlign='LEFT',
        )
        parties_table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.extend([parties_table, Spacer(1, 12)])

        item_rows = [['内容', '数量', '単価', '金額']]
        item_rows.extend(
            [
                item.description,
                str(item.quantity),
                self._format_jpy(item.unit_price),
                self._format_jpy(item.total),
            ]
            for item in items
        )
        items_table = Table(item_rows, colWidths=[88 * mm, 18 * mm, 35 * mm, 35 * mm], hAlign='LEFT')
        items_table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), self.heading_font_name),
                    ('FONTNAME', (0, 1), (-1, -1), self.body_font_name),
                    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.extend([items_table, Spacer(1, 12)])

        totals_table = Table(
            [
                ['小計', self._format_jpy(subtotal)],
                ['消費税 (10%)', self._format_jpy(tax)],
                ['合計', self._format_jpy(total)],
            ],
            colWidths=[35 * mm, 35 * mm],
            hAlign='RIGHT',
        )
        totals_table.setStyle(
            TableStyle(
                [
                    ('FONTNAME', (0, 0), (-1, -1), self.body_font_name),
                    ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                    ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#dcfce7')),
                    ('FONTNAME', (0, 2), (-1, 2), self.heading_font_name),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.extend(
            [
                totals_table,
                Spacer(1, 12),
                Paragraph('このプレビューは、請求書 PDF を日本語で生成できることを確認するためのサンプルです。', muted_style),
            ]
        )

        document.build(story)
        return buffer.getvalue()

    @classmethod
    def _register_fonts(cls) -> None:
        registered_font_names = pdfmetrics.getRegisteredFontNames()
        if cls.heading_font_name not in registered_font_names:
            pdfmetrics.registerFont(UnicodeCIDFont(cls.heading_font_name))
        if cls.body_font_name not in registered_font_names:
            pdfmetrics.registerFont(UnicodeCIDFont(cls.body_font_name))

    @staticmethod
    def _format_jpy(amount: Decimal) -> str:
        return f'{amount:,.0f} 円'

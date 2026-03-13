from decimal import Decimal

from django.db import models

from .invoice import Invoice
from .quote_item import QuoteItem
from .shared import ZERO_DECIMAL, quantize_amount
from .time_stamped_model import TimeStampedModel


class InvoiceItem(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, verbose_name='請求書', related_name='items', on_delete=models.CASCADE)
    quote_item = models.ForeignKey(QuoteItem, verbose_name='元見積明細', related_name='invoice_items', on_delete=models.SET_NULL, null=True, blank=True)
    display_order = models.PositiveIntegerField('表示順', default=1)
    description = models.CharField('内容', max_length=255)
    unit_label = models.CharField('単位', max_length=50, blank=True)
    quantity = models.DecimalField('数量', max_digits=10, decimal_places=2, default=Decimal('1.00'))
    unit_price = models.DecimalField('単価', max_digits=12, decimal_places=2)
    total_amount = models.DecimalField('金額', max_digits=12, decimal_places=2, default=ZERO_DECIMAL)
    notes = models.TextField('備考', blank=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = '請求明細'
        verbose_name_plural = '請求明細'

    def __str__(self) -> str:
        return f'{self.invoice.invoice_number} / {self.description}'

    def save(self, *args, **kwargs):
        self.total_amount = quantize_amount(self.quantity * self.unit_price)
        super().save(*args, **kwargs)

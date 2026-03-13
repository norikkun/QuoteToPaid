from django.db import models

from .choices import PaymentMethod, PaymentStatus
from .invoice import Invoice
from .shared import ZERO_DECIMAL, quantize_amount
from .time_stamped_model import TimeStampedModel


class Payment(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, verbose_name='請求書', related_name='payments', on_delete=models.CASCADE)
    received_on = models.DateField('入金日')
    amount = models.DecimalField('入金額', max_digits=12, decimal_places=2)
    fee_amount = models.DecimalField('手数料', max_digits=12, decimal_places=2, default=ZERO_DECIMAL)
    method = models.CharField('入金方法', max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.BANK_TRANSFER)
    status = models.CharField('ステータス', max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.RECEIVED)
    reference_number = models.CharField('参照番号', max_length=100, blank=True)
    notes = models.TextField('備考', blank=True)

    class Meta:
        ordering = ['-received_on', '-id']
        verbose_name = '入金'
        verbose_name_plural = '入金'

    def __str__(self) -> str:
        return f'{self.invoice.invoice_number} / {self.received_on}'

    @property
    def net_amount(self):
        return quantize_amount(self.amount - self.fee_amount)
